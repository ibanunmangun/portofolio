(() => {
  const asset = (name) => `../data/aceh-tamiang-flood/processed/${name}`;
  const state = document.getElementById('map-state');
  const heading = document.getElementById('detail-heading');
  const copy = document.getElementById('detail-copy');
  const details = document.getElementById('detail-list');
  const list = document.getElementById('area-list');
  const imageryToggle = document.getElementById('reference-imagery');
  const imageryNotice = document.getElementById('imagery-notice');
  const imageryAttribution = document.getElementById('imagery-attribution');
  const showState = (message, error = false) => {
    state.hidden = false;
    state.textContent = message;
    state.classList.toggle('error', error);
  };
  const hideState = () => { state.hidden = true; };
  const getJson = async (name) => {
    const response = await fetch(asset(name));
    if (!response.ok) throw new Error(`${name} could not be loaded`);
    return response.json();
  };
  const setDetails = (feature) => {
    const p = feature.properties;
    const named = p.report_state === 'named_in_report';
    heading.textContent = p.subdistrict;
    copy.textContent = named
      ? 'This subdistrict was named in the 16 November 2026 report snapshot.'
      : 'This subdistrict was not named in the 16 November report snapshot. That does not establish that it was unaffected.';
    const entries = [
      ['Report status', named ? 'Named in report snapshot' : 'Not named in this snapshot'],
      ['Regency', p.regency],
      ['Report date', p.report_date],
      ['Map meaning', named ? 'Reported administrative footprint' : 'Administrative reference context'],
    ];
    details.replaceChildren();
    entries.forEach(([term, value]) => {
      const row = document.createElement('div');
      const dt = document.createElement('dt');
      const dd = document.createElement('dd');
      dt.textContent = term;
      dd.textContent = value;
      row.append(dt, dd);
      details.append(row);
    });
    details.hidden = false;
  };
  const init = async () => {
    try {
      showState('Loading report footprint.');
      const [admin, report, metadata] = await Promise.all([
        getJson('aceh-tamiang-admin3.geojson'),
        getJson('reported-impact-footprint.geojson'),
        getJson('metadata.json'),
      ]);
      if (!admin.features.length || !report.features.length) {
        showState('This report snapshot has no displayable administrative areas.');
        return;
      }
      const terrain = metadata.terrain_relief;
      if (!terrain || !Array.isArray(terrain.bounds_wgs84) || terrain.bounds_wgs84.length !== 4) {
        throw new Error('Terrain-relief metadata is incomplete');
      }
      const [west, south, east, north] = terrain.bounds_wgs84;
      const terrainBounds = L.latLngBounds([[south, west], [north, east]]);
      const map = L.map('map', {
        zoomControl: true,
        attributionControl: true,
        maxBounds: terrainBounds,
        maxBoundsViscosity: 1.0,
      });
      map.attributionControl.setPrefix(false);
      L.imageOverlay(asset(terrain.output), [[south, west], [north, east]], {
        opacity: 0.34,
        interactive: false,
        attribution: terrain.attribution,
      }).addTo(map);
      const imagery = L.tileLayer(
        'https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_TrueColor/default/2026-11-16/GoogleMapsCompatible_Level9/{z}/{y}/{x}.jpg',
        { maxNativeZoom: 9, maxZoom: 12, opacity: 0.42, attribution: 'NASA GIBS, MODIS Terra, 16 Nov 2026' },
      );
      const updateImagery = () => {
        const active = imageryToggle.checked;
        if (active) imagery.addTo(map);
        else map.removeLayer(imagery);
        imageryNotice.hidden = !active;
        imageryAttribution.hidden = !active;
      };
      imageryToggle.addEventListener('change', updateImagery);
      const adminLayer = L.geoJSON(admin, {
        style: { color: '#718071', weight: 1, fillColor: '#1b241c', fillOpacity: 0.18 },
        onEachFeature: (feature, layer) => layer.on('click', () => setDetails(feature)),
      }).addTo(map);
      const reportLayer = L.geoJSON(report, {
        style: { color: '#ffd59b', weight: 2, fillColor: '#cc653f', fillOpacity: 0.72 },
        onEachFeature: (feature, layer) => {
          layer.on('click', () => setDetails(feature));
          const tooltip = document.createElement('span');
          tooltip.textContent = feature.properties.subdistrict;
          layer.bindTooltip(tooltip, { sticky: true, direction: 'top' });
        },
      }).addTo(map);
      const bounds = adminLayer.getBounds();
      const viewPadding = [20, 20];
      map.fitBounds(bounds, { padding: viewPadding });
      map.setMinZoom(map.getZoom());
      document.getElementById('reset-map').addEventListener('click', () => map.fitBounds(bounds, { padding: viewPadding }));
      report.features.sort((a, b) => a.properties.subdistrict.localeCompare(b.properties.subdistrict)).forEach((feature) => {
        const button = document.createElement('button');
        button.type = 'button';
        button.textContent = feature.properties.subdistrict;
        button.addEventListener('click', () => {
          setDetails(feature);
          const layer = reportLayer.getLayers().find((item) => item.feature.properties.admin_id === feature.properties.admin_id);
          if (layer) map.fitBounds(layer.getBounds(), { padding: [35, 35], maxZoom: 10 });
        });
        list.append(button);
      });
      updateImagery();
      hideState();
      document.getElementById('map').setAttribute('aria-busy', 'false');
    } catch (error) {
      console.error(error);
      showState('The report footprint could not be loaded. Refresh the page or return to the portfolio home.', true);
      document.getElementById('map').setAttribute('aria-busy', 'false');
    }
  };
  window.addEventListener('DOMContentLoaded', init);
})();
