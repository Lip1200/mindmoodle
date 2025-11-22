/**
 * Copilot Companion Script
 * Extracts the 'companion' parameter from URL and injects it into chat context
 */

(function() {
    'use strict';
    
    console.log('🐾 Copilot Companion Script loaded');
    
    // Extract companion parameter from URL
    function getCompanionFromURL() {
        const urlParams = new URLSearchParams(window.location.search);
        const companion = urlParams.get('companion');
        
        // Validate companion
        const validCompanions = ['dog', 'cat', 'eagle', 'raccoon', 'panda', 'dragon'];
        
        if (companion && validCompanions.includes(companion)) {
            console.log(`🎯 Companion detected: ${companion}`);
            return companion;
        }
        
        // Check localStorage as fallback
        try {
            const stored = localStorage.getItem('mh_companion_animal');
            if (stored && validCompanions.includes(stored)) {
                console.log(`💾 Companion from storage: ${stored}`);
                return stored;
            }
        } catch (e) {
            console.warn('Could not access localStorage:', e);
        }
        
        console.log('🐶 Using default companion: dog');
        return 'dog';
    }
    
    // Inject companion into Chainlit context
    function injectCompanion() {
        const companion = getCompanionFromURL();
        
        // Store in localStorage for persistence
        try {
            localStorage.setItem('mh_companion_animal', companion);
        } catch (e) {
            console.warn('Could not save to localStorage:', e);
        }
        
        // Attempt to inject into window context for backend access
        window.MENTAL_HEALTH_COMPANION = companion;
        
        // Intercept WebSocket connection to inject companion metadata
        const originalWebSocket = window.WebSocket;
        window.WebSocket = function(url, protocols) {
            console.log('🔌 WebSocket intercepted, injecting companion:', companion);
            
            // Add companion as query parameter to WebSocket URL
            const separator = url.includes('?') ? '&' : '?';
            const modifiedUrl = url + separator + 'companion=' + encodeURIComponent(companion);
            
            const ws = new originalWebSocket(modifiedUrl, protocols);
            
            // Hook into send to inject companion in first message
            const originalSend = ws.send.bind(ws);
            let firstMessage = true;
            ws.send = function(data) {
                if (firstMessage) {
                    try {
                        const parsed = JSON.parse(data);
                        if (!parsed.metadata) parsed.metadata = {};
                        parsed.metadata.companion = companion;
                        data = JSON.stringify(parsed);
                        console.log('✅ Companion injected into first WS message');
                    } catch (e) {
                        console.warn('Could not parse WS message:', e);
                    }
                    firstMessage = false;
                }
                return originalSend(data);
            };
            
            return ws;
        };
        
        console.log('✅ Companion injection setup complete');
    }
    
    // Run on load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', injectCompanion);
    } else {
        injectCompanion();
    }
})();
