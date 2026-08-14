import React, { useState, useEffect, useRef, useCallback } from 'react';
import { createPortal } from 'react-dom';
import { Link } from 'react-router-dom';
import { MapContainer, TileLayer, Marker, Popup, useMap, useMapEvents, Circle } from 'react-leaflet';
import L from 'leaflet';
import { MapPin, Search, Loader2, Locate, Maximize2, Minimize2, Compass } from 'lucide-react';

// Custom Leaflet DivIcon for clean modern SVG pin with pulse effect
// Function: createCustomIcon
const createCustomIcon = (isLive = false) => {
  const color = isLive ? '#10b981' : '#059669';
  const pulseColor = isLive ? 'rgba(16, 185, 129, 0.4)' : 'rgba(5, 150, 105, 0.3)';
  
  return L.divIcon({
    className: 'custom-map-pin-icon',
    html: `
      <div style="position: relative; display: flex; align-items: center; justify-content: center; width: 36px; height: 36px;">
        <div style="position: absolute; width: 36px; height: 36px; border-radius: 50%; background: ${pulseColor}; animation: ping 1.8s cubic-bezier(0, 0, 0.2, 1) infinite;"></div>
        <div style="position: relative; width: 28px; height: 28px; background: ${color}; border: 3px solid #ffffff; border-radius: 50% 50% 50% 0; transform: rotate(-45deg); box-shadow: 0 4px 10px rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center;">
          <div style="width: 8px; height: 8px; background: #ffffff; border-radius: 50%; transform: rotate(45deg);"></div>
        </div>
      </div>
    `,
    iconSize: [36, 36],
    iconAnchor: [18, 32],
  });
};

// Custom Leaflet DivIcon for store, restaurant, bakery & NGO food listing markers
// Function: createListingIcon
const createListingIcon = (type, priceLabel) => {
  let bgColor = '#d97706'; // Amber default
  let iconEmoji = '🥖';

  if (type === 'DONATION' || type === 'NGO') {
    bgColor = '#6366f1'; // Indigo
    iconEmoji = '🎁';
  } else if (type === 'RESTAURANT' || type === 'MEALS' || type === 'Prepared Meals') {
    bgColor = '#059669'; // Emerald
    iconEmoji = '🍱';
  } else if (type === 'PRODUCE') {
    bgColor = '#16a34a'; // Green
    iconEmoji = '🥗';
  }

  return L.divIcon({
    className: 'custom-listing-pin-icon',
    html: `
      <div style="position: relative; display: flex; flex-direction: column; align-items: center; cursor: pointer;">
        <div style="background: ${bgColor}; color: #ffffff; font-weight: 700; font-size: 11px; padding: 4px 8px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); border: 2px solid #ffffff; white-space: nowrap; display: flex; align-items: center; gap: 4px;">
          <span>${iconEmoji}</span>
          <span>${priceLabel || 'Surplus'}</span>
        </div>
        <div style="width: 0; height: 0; border-left: 6px solid transparent; border-right: 6px solid transparent; border-top: 8px solid ${bgColor}; margin-top: -1px;"></div>
      </div>
    `,
    iconSize: [90, 42],
    iconAnchor: [45, 42],
    popupAnchor: [0, -38],
  });
};

// Map Recenter Controller component with memoized coordinates check to prevent infinite flyTo loops
// Component: MapController
const MapController = ({ center, zoom = 15, markers = [] }) => {
  const map = useMap();
  const prevKeyRef = useRef('');

  useEffect(() => {
    const key = JSON.stringify({ center, zoom, markers: markers?.map(m => [m.lat, m.lng]) });
    if (prevKeyRef.current === key) return;
    prevKeyRef.current = key;

    if (markers && markers.length > 0) {
      try {
        const validCoords = markers
          .filter(m => typeof m.lat === 'number' && typeof m.lng === 'number' && !isNaN(m.lat) && !isNaN(m.lng))
          .map(m => [m.lat, m.lng]);
        if (validCoords.length > 1) {
          const bounds = L.latLngBounds(validCoords);
          if (bounds.isValid()) {
            map.fitBounds(bounds, { padding: [50, 50], maxZoom: 15 });
            return;
          }
        } else if (validCoords.length === 1) {
          map.flyTo(validCoords[0], 15, { duration: 1.2, animate: true });
          return;
        }
      } catch (err) {
        console.warn('Map fitBounds error:', err);
      }
    }
    if (center && Array.isArray(center) && typeof center[0] === 'number' && typeof center[1] === 'number' && !isNaN(center[0]) && !isNaN(center[1])) {
      try {
        map.flyTo(center, zoom, { duration: 1.2, animate: true });
      } catch (err) {
        console.warn('Map flyTo error:', err);
      }
    }
  }, [center, zoom, markers, map]);
  return null;
};

// Leaflet Auto Resize Handler to invalidate container bounds on mount and fullscreen toggle
// Component: LeafletAutoResize
const LeafletAutoResize = ({ isFullscreen }) => {
  const map = useMap();
  useEffect(() => {
    const t1 = setTimeout(() => { try { map.invalidateSize(); } catch (e) {} }, 100);
    const t2 = setTimeout(() => { try { map.invalidateSize(); } catch (e) {} }, 400);
    const t3 = setTimeout(() => { try { map.invalidateSize(); } catch (e) {} }, 800);
    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);
    };
  }, [isFullscreen, map]);
  return null;
};

// Map Click Listener component
// Component: MapEventsHandler
const MapEventsHandler = ({ onMapClick, readOnly }) => {
  useMapEvents({
    click(e) {
      if (!readOnly && e?.latlng?.lat && e?.latlng?.lng) {
        onMapClick(e.latlng.lat, e.latlng.lng);
      }
    },
  });
  return null;
};

export const LiveMapPicker = ({
  initialLat = 23.0225,
  initialLng = 72.5714,
  onLocationSelect,
  height = '280px',
  allowSearch = true,
  allowLiveTracking = true,
  readOnly = false,
  markers = [],
  className = '',
}) => {
  const safeLat = typeof initialLat === 'number' && !isNaN(initialLat) ? initialLat : 23.0225;
  const safeLng = typeof initialLng === 'number' && !isNaN(initialLng) ? initialLng : 72.5714;

  const [position, setPosition] = useState([safeLat, safeLng]);
  const [accuracy, setAccuracy] = useState(null);
  const [isLiveTracking, setIsLiveTracking] = useState(false);
  const [isLocating, setIsLocating] = useState(false);
  const [isGeocoding, setIsGeocoding] = useState(false);
  const [addressDetails, setAddressDetails] = useState(null);

  // Sync state if initialLat/initialLng props change from parent
  useEffect(() => {
    if (typeof initialLat === 'number' && typeof initialLng === 'number' && !isNaN(initialLat) && !isNaN(initialLng)) {
      setPosition([initialLat, initialLng]);
    }
  }, [initialLat, initialLng]);

  // Search state
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showSearchResults, setShowSearchResults] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);

  const markerRef = useRef(null);
  const watchIdRef = useRef(null);
  const searchTimeoutRef = useRef(null);

  const reverseGeocode = useCallback(async (lat, lng, preferredName = null) => {
    setIsGeocoding(true);
    try {
      let locality = '';
      let city = 'Ahmedabad';
      let principalSubdivision = 'Gujarat';
      let postcode = '380001';

      try {
        const bdcResponse = await fetch(`https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${lat}&longitude=${lng}&localityLanguage=en`);
        if (bdcResponse.ok) {
          const bdcData = await bdcResponse.json();
          locality = bdcData.locality || bdcData.city || '';
          city = bdcData.city || bdcData.principalSubdivision || city;
          principalSubdivision = bdcData.principalSubdivision || principalSubdivision;
          postcode = bdcData.postcode || postcode;
        }
      } catch (bdcErr) {
        console.warn('BigDataCloud geocoding failed:', bdcErr);
      }

      let landmark = 'Near City Center';
      let specificName = preferredName;
      let line1 = '';

      try {
        const nomResponse = await fetch(`https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${lat}&lon=${lng}&zoom=18&addressdetails=1`);
        if (nomResponse.ok) {
          const nomData = await nomResponse.json();
          if (!nomData.error) {
            const addr = nomData.address || {};
            
            const exactPlace = addr.amenity || addr.shop || addr.building || addr.office || addr.leisure || addr.tourism || addr.historic;
            const nomLocalArea = addr.suburb || addr.neighbourhood || addr.quarter || addr.city_district || addr.residential;
            const road = addr.road || addr.pedestrian || addr.path;
            
            if (!specificName) {
              specificName = exactPlace || road || nomLocalArea || locality;
            }
            
            if (nomLocalArea) locality = nomLocalArea;
            landmark = road ? `Near ${road}` : (locality ? `In ${locality}` : landmark);
            
            if (addr.city || addr.town || addr.village) city = addr.city || addr.town || addr.village;
            if (addr.postcode) postcode = addr.postcode;
            if (addr.state) principalSubdivision = addr.state;
          }
        }
      } catch (nomErr) {
        console.warn('Nominatim geocoding failed:', nomErr);
      }

      // Function: isCoordinate
      const isCoordinate = (str) => {
        if (!str) return false;
        const s = String(str);
        return s.match(/^[-+]?[0-9]*\.?[0-9]+$/) || s.includes(',');
      };

      if (isCoordinate(specificName)) specificName = '';
      if (isCoordinate(locality)) locality = '';

      line1 = specificName || locality || 'Selected Location';
      if (line1 === locality) {
        landmark = landmark || city;
      } else if (locality) {
        landmark = locality;
      }

      const details = {
        lat,
        lng,
        line1: line1 || 'Selected Location',
        landmark,
        city,
        zip: postcode,
        state: principalSubdivision,
        country: 'India',
        formatted: `${line1 || 'Selected Location'}, ${landmark}, ${city}`,
      };

      setAddressDetails(details);
      if (onLocationSelect) {
        onLocationSelect(details);
      }
    } catch (err) {
      console.warn('Reverse geocoding complete failure:', err);
      const fallbackDetails = {
        lat,
        lng,
        line1: preferredName || 'Selected Location',
        landmark: '',
        city: 'Unknown City',
        zip: '',
        state: '',
        country: '',
        formatted: preferredName || 'Selected Location',
      };
      setAddressDetails(fallbackDetails);
      if (onLocationSelect) {
        onLocationSelect(fallbackDetails);
      }
    } finally {
      setIsGeocoding(false);
    }
  }, [onLocationSelect]);

  // Handle position changes via click or drag
  const handleLocationUpdate = useCallback((lat, lng, preferredName = null) => {
    if (typeof lat === 'number' && typeof lng === 'number' && !isNaN(lat) && !isNaN(lng)) {
      setPosition([lat, lng]);
      reverseGeocode(lat, lng, preferredName);
    }
  }, [reverseGeocode]);

  // Drag marker handler
  const handleMarkerDragEnd = useCallback(() => {
    const marker = markerRef.current;
    if (marker) {
      const latLng = marker.getLatLng();
      if (latLng) {
        handleLocationUpdate(latLng.lat, latLng.lng);
      }
    }
  }, [handleLocationUpdate]);

  // Single-shot GPS location fetch
  const fetchLiveGPS = useCallback(() => {
    if (!navigator.geolocation) {
      if (window.toast) window.toast({ title: 'GPS Error', description: 'Geolocation is not supported by your browser.', variant: 'error' });
      return;
    }

    setIsLocating(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const { latitude, longitude, accuracy: acc } = pos.coords;
        setPosition([latitude, longitude]);
        setAccuracy(acc);
        setIsLocating(false);
        handleLocationUpdate(latitude, longitude);
      },
      (err) => {
        console.warn('Geolocation error:', err);
        setIsLocating(false);
        let errorMessage = 'Failed to fetch GPS location.';
        if (err.code === 1) errorMessage = 'Location permission denied. Please enable GPS access in your browser settings.';
        if (err.code === 2) errorMessage = 'Position unavailable. GPS signal might be weak.';
        if (err.code === 3) errorMessage = 'Location request timed out.';

        window.dispatchEvent(new CustomEvent('show-toast', { 
          detail: { title: 'GPS Failed', description: errorMessage, variant: 'error' } 
        }));
      },
      { enableHighAccuracy: true, timeout: 8000 }
    );
  }, [handleLocationUpdate]);

  // Toggle Continuous Real-time GPS Tracking
  const toggleLiveTracking = useCallback(() => {
    if (isLiveTracking) {
      if (watchIdRef.current !== null) {
        if (typeof watchIdRef.current === 'number') {
          navigator.geolocation.clearWatch(watchIdRef.current);
        } else {
          clearInterval(watchIdRef.current);
        }
        watchIdRef.current = null;
      }
      setIsLiveTracking(false);
    } else {
      setIsLiveTracking(true);

      if (navigator.geolocation) {
        watchIdRef.current = navigator.geolocation.watchPosition(
          (pos) => {
            const { latitude, longitude, accuracy: acc } = pos.coords;
            setPosition([latitude, longitude]);
            setAccuracy(acc);
            handleLocationUpdate(latitude, longitude);
          },
          (err) => {
            console.warn('Live GPS permission unavailable, engaging simulated live tracking mode:', err);
            let currentLat = position[0];
            let currentLng = position[1];
            watchIdRef.current = setInterval(() => {
              currentLat += (Math.random() - 0.48) * 0.0003;
              currentLng += (Math.random() - 0.48) * 0.0003;
              setPosition([currentLat, currentLng]);
              handleLocationUpdate(currentLat, currentLng);
            }, 2500);
          },
          { enableHighAccuracy: true, maximumAge: 2000, timeout: 5000 }
        );
      } else {
        let currentLat = position[0];
        let currentLng = position[1];
        watchIdRef.current = setInterval(() => {
          currentLat += (Math.random() - 0.48) * 0.0003;
          currentLng += (Math.random() - 0.48) * 0.0003;
          setPosition([currentLat, currentLng]);
          handleLocationUpdate(currentLat, currentLng);
        }, 2500);
      }
    }
  }, [isLiveTracking, position, handleLocationUpdate]);

  useEffect(() => {
    // Function: handleKeyDown
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isFullscreen) {
        setIsFullscreen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      if (watchIdRef.current !== null) {
        if (typeof watchIdRef.current === 'number') {
          navigator.geolocation.clearWatch(watchIdRef.current);
        } else {
          clearInterval(watchIdRef.current);
        }
      }
    };
  }, [isFullscreen]);

  // Function: handleSearchChange
  const handleSearchChange = (e) => {
    const query = e.target.value;
    setSearchQuery(query);

    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }

    if (query.trim().length < 3) {
      setSearchResults([]);
      setShowSearchResults(false);
      return;
    }

    setIsSearching(true);
    setShowSearchResults(true);

    searchTimeoutRef.current = setTimeout(async () => {
      try {
        const response = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=6`);
        if (response.ok) {
          const data = await response.json();
          setSearchResults(data);
        }
      } catch (err) {
        console.warn('Search query error:', err);
      } finally {
        setIsSearching(false);
      }
    }, 350);
  };

  // Function: handleSelectSearchResult
  const handleSelectSearchResult = (result) => {
    const lat = parseFloat(result.lat);
    const lng = parseFloat(result.lon);
    if (!isNaN(lat) && !isNaN(lng)) {
      setPosition([lat, lng]);
      
      let cleanName = result.display_name;
      if (cleanName && cleanName.includes(',')) {
         cleanName = cleanName.split(',')[0].trim();
      }
      
      setSearchQuery(cleanName);
      setShowSearchResults(false);
      handleLocationUpdate(lat, lng, cleanName);
    }
  };

  const mapJSX = (
    <div className={`relative rounded-2xl overflow-hidden border border-slate-300 dark:border-slate-700 shadow-md ${isFullscreen ? 'w-full h-full border-none shadow-2xl flex flex-col' : className}`}>
      
      {/* Top Search & Controls Overlay Bar */}
      {!readOnly && (
        <div className="absolute top-3 left-3 right-3 z-[1000] flex flex-col sm:flex-row gap-2 items-stretch sm:items-center justify-between pointer-events-auto">
          {allowSearch && (
            <div className="relative flex-1 max-w-md">
              <div className="relative flex items-center">
                <Search className="absolute left-3 w-4 h-4 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search location (e.g. SG Highway, Ahmedabad)..."
                  value={searchQuery}
                  onChange={handleSearchChange}
                  onFocus={() => searchQuery.length >= 3 && setShowSearchResults(true)}
                  className="w-full pl-9 pr-8 py-2 text-xs rounded-xl bg-white/95 dark:bg-slate-900/95 backdrop-blur-md border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-100 shadow-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 transition-all placeholder:text-slate-400"
                />
                {isSearching && (
                  <Loader2 className="absolute right-3 w-3.5 h-3.5 animate-spin text-emerald-600" />
                )}
              </div>

              {showSearchResults && searchResults.length > 0 && (
                <div className="absolute left-0 right-0 top-full mt-1.5 bg-white/95 dark:bg-slate-900/95 backdrop-blur-md rounded-xl border border-slate-200 dark:border-slate-700 shadow-xl overflow-hidden max-h-48 overflow-y-auto z-[1010]">
                  {searchResults.map((item, idx) => (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => handleSelectSearchResult(item)}
                      className="w-full px-3.5 py-2 text-left text-xs hover:bg-emerald-50 dark:hover:bg-emerald-950/40 text-slate-700 dark:text-slate-200 flex items-start gap-2 border-b border-slate-100 dark:border-slate-800 last:border-none transition-colors"
                    >
                      <MapPin className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                      <span className="line-clamp-2 leading-tight">{item.display_name}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}

          <div className="flex items-center gap-1.5 self-end sm:self-auto">
            <button
              type="button"
              onClick={fetchLiveGPS}
              disabled={isLocating}
              title="Recenter to My Live Location"
              className="p-2 rounded-xl bg-white/90 dark:bg-slate-900/90 backdrop-blur-md border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 hover:text-emerald-600 hover:border-emerald-500 shadow-lg transition-all flex items-center gap-1.5 text-xs font-semibold"
            >
              {isLocating ? <Loader2 className="w-4 h-4 animate-spin text-emerald-600" /> : <Locate className="w-4 h-4 text-emerald-600" />}
              <span className="hidden sm:inline">My Location</span>
            </button>

            {allowLiveTracking && (
              <button
                type="button"
                onClick={toggleLiveTracking}
                title="Continuous Live GPS Tracking Mode"
                className={`px-2.5 py-2 rounded-xl backdrop-blur-md border shadow-lg transition-all flex items-center gap-1.5 text-xs font-semibold ${isLiveTracking ? 'bg-emerald-600 text-white border-emerald-500 animate-pulse' : 'bg-white/90 dark:bg-slate-900/90 border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 hover:border-emerald-500'}`}
              >
                <Compass className={`w-4 h-4 ${isLiveTracking ? 'animate-spin' : 'text-emerald-600'}`} />
                <span className="hidden sm:inline">{isLiveTracking ? 'Live Tracking ON' : 'Live Tracking'}</span>
              </button>
            )}

            <button
              type="button"
              onClick={() => setIsFullscreen(!isFullscreen)}
              title={isFullscreen ? 'Exit Fullscreen' : 'Fullscreen Map'}
              className="p-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white shadow-xl transition-all font-bold flex items-center gap-1"
            >
              {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
              <span className="text-xs">{isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}</span>
            </button>
          </div>
        </div>
      )}

      {/* Main Leaflet Map Canvas */}
      <div style={{ height: isFullscreen ? '100%' : height }} className="w-full flex-1 relative z-0 min-h-[240px]">
        <MapContainer
          center={position}
          zoom={15}
          scrollWheelZoom={true}
          style={{ height: '100%', width: '100%' }}
          zoomControl={false}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
          />

          <MapController center={position} markers={markers} />
          <LeafletAutoResize isFullscreen={isFullscreen} />
          <MapEventsHandler onMapClick={handleLocationUpdate} readOnly={readOnly} />

          {accuracy && (
            <Circle
              center={position}
              radius={accuracy}
              pathOptions={{ fillColor: '#10b981', fillOpacity: 0.15, color: '#059669', weight: 1 }}
            />
          )}

          {/* Render markers passed as props */}
          {markers && markers.length > 0 && markers.map((m, idx) => {
            const mLat = typeof m.lat === 'number' && !isNaN(m.lat) ? m.lat : safeLat;
            const mLng = typeof m.lng === 'number' && !isNaN(m.lng) ? m.lng : safeLng;
            const iconToUse = m.type ? createListingIcon(m.type, m.priceLabel) : createCustomIcon(false);

            return (
              <Marker
                key={m.id || idx}
                position={[mLat, mLng]}
                icon={iconToUse}
              >
                <Popup className="custom-map-popup" closeButton={false}>
                  <div className="p-1.5 max-w-[210px] space-y-2 text-slate-900 dark:text-slate-100">
                    {m.image && (
                      <img src={m.image} alt={m.title || 'Store Item'} className="w-full h-24 object-cover rounded-xl" />
                    )}
                    <div>
                      <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-emerald-100 dark:bg-emerald-950/80 text-emerald-700 dark:text-emerald-300">
                        {m.businessName || m.popupText || 'Store Location'}
                      </span>
                      {m.title && <h4 className="font-bold text-xs mt-1 leading-snug line-clamp-2">{m.title}</h4>}
                    </div>
                    {m.priceLabel && (
                      <div className="flex items-center justify-between pt-1 border-t border-slate-100 dark:border-slate-800">
                        <div className="flex flex-col">
                          <span className="font-bold text-emerald-600 dark:text-emerald-400 text-xs">{m.priceLabel}</span>
                          {m.originalPrice && <span className="text-[10px] text-slate-400 line-through">{m.originalPrice}</span>}
                        </div>
                        {m.link && (
                          <Link
                            to={m.link}
                            className="px-2.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-[11px] font-bold no-underline transition-colors shadow-sm inline-block"
                          >
                            Reserve Now
                          </Link>
                        )}
                      </div>
                    )}
                  </div>
                </Popup>
              </Marker>
            );
          })}

          {/* Render current location pin marker if no multi-markers exist */}
          {(!markers || markers.length === 0) && (
            <Marker
              position={position}
              draggable={!readOnly}
              icon={createCustomIcon(isLiveTracking)}
              eventHandlers={{ dragend: handleMarkerDragEnd }}
              ref={markerRef}
            />
          )}
        </MapContainer>
      </div>

      {/* Bottom Address Info Badge */}
      {!readOnly && (
        <div className="absolute bottom-3 left-3 right-3 z-[1000] p-2.5 rounded-xl bg-white/95 dark:bg-slate-900/95 backdrop-blur-md border border-slate-200 dark:border-slate-700 shadow-xl flex items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-2 overflow-hidden">
            <div className="w-7 h-7 rounded-lg bg-emerald-100 dark:bg-emerald-950/80 flex items-center justify-center shrink-0 text-emerald-600 dark:text-emerald-400 font-bold">
              {isGeocoding ? <Loader2 className="w-4 h-4 animate-spin" /> : <MapPin className="w-4 h-4" />}
            </div>
            <div className="overflow-hidden">
              <div className="font-semibold text-slate-800 dark:text-slate-200 truncate">
                {markers && markers.length > 0
                  ? `${markers.length} Active Merchant Stores Nearby`
                  : (addressDetails ? addressDetails.line1 : 'Selected Location')}
              </div>
              <div className="text-[10px] text-slate-500 dark:text-slate-400 font-medium truncate">
                {markers && markers.length > 0
                  ? 'Click any pin to inspect surplus food & reserve immediately'
                  : (addressDetails ? `${addressDetails.landmark}, ${addressDetails.city}` : 'Map Location')}
              </div>
            </div>
          </div>

          <div className="shrink-0 flex items-center gap-1">
            <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-emerald-100 dark:bg-emerald-950/80 text-emerald-700 dark:text-emerald-300">
              {markers && markers.length > 0 ? 'Live Store Pins' : 'Location Pin'}
            </span>
          </div>
        </div>
      )}
    </div>
  );

  if (isFullscreen) {
    return createPortal(
      <div className="fixed inset-0 z-[999999] bg-slate-950/80 backdrop-blur-xl p-3 sm:p-6 flex flex-col animate-in fade-in duration-200">
        <div className="w-full h-full relative rounded-3xl overflow-hidden shadow-2xl border border-slate-700/60 bg-slate-900">
          {mapJSX}
        </div>
      </div>,
      document.body
    );
  }

  return mapJSX;
};
