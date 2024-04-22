/**
 * Initializes the functionality to open and close a modal window based on URL parameters.
 * This function sets up event listeners for opening and closing the modal. It also ensures
 * that the modal's display state is synchronized with the appropriate URL parameter.
 *
 * @param {string} modalURLParam - The URL parameter name that controls the modal's visibility.
 * @param {string} modalID - The DOM ID of the modal element that is to be shown or hidden.
 * @param {array} openModelIDs - Lis DOM ID of the element that, when clicked, opens the modal.
 * @param {array} closeModalIDs - The DOM ID of the element that, when clicked, closes the modal.
 */
function setModal(modalURLParam, modalID, openModelIDs, closeModalIDs) {

    for (closeModalID of closeModalIDs) {
        document.getElementById(closeModalID).onclick = function() {
            const url = new URL(window.location);
            url.searchParams.delete(modalURLParam);
            window.history.pushState({}, '', url);
            toggleModalDisplay()
        }
    }
    
    for (openModelID of openModelIDs) {
        document.getElementById(openModelID).onclick = function() {
            const url = new URL(window.location);
            url.searchParams.set(modalURLParam, 'true');
            window.history.pushState({}, '', url);
            toggleModalDisplay();
        }
    }
        
    // Function to toggle modal display based on URL parameter
    function toggleModalDisplay() {
        const showModal = new URLSearchParams(window.location.search).get(modalURLParam);
        const modalDisplay = showModal === 'true' ? 'block' : 'none';
        document.getElementById(modalID).style.display = modalDisplay;
    }
    
    // Check modal state on page load or navigation changes
    document.addEventListener("DOMContentLoaded", toggleModalDisplay);
    window.addEventListener("popstate", toggleModalDisplay);
}
