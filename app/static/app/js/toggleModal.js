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

// class ModalManager {
//     constructor(modalURLParam, modalID, openModalIDs, closeModalIDs) {
//         this.modalURLParam = modalURLParam;
//         this.modalID = modalID;
//         this.openModalIDs = openModalIDs;
//         this.closeModalIDs = closeModalIDs;
//         this.initialize();
//     }

//     initialize() {
//         // Set up the event listeners to open the modal
//         if (this.openModalIDs !== null) {
//             for (const openModalID of this.openModalIDs) {
//                 document.getElementById(openModalID).onclick = () => {
//                     this.openModal("true");
//                 };
//             }
//         }

//         // Set up the event listeners to close the modal
//         if (this.closeModalIDs !== null) {
//             for (const closeModalID of this.closeModalIDs) {
//                 document.getElementById(closeModalID).onclick = () => {
//                     this.closeModal();
//                 };
//             }
//         }

//         // Ensure that the modal display is correct on page load or navigation
//         document.addEventListener("DOMContentLoaded", () => this.checkModalDisplay());
//         window.addEventListener("popstate", () => this.setModalDisplay());
//     }

//     openModal(URLParamValue) {
//         const url = new URL(window.location);
//         url.searchParams.set(this.modalURLParam, URLParamValue);
//         window.history.pushState({}, '', url);
//         this.setModalDisplay();
//     }

//     closeModal() {
//         const url = new URL(window.location);
//         url.searchParams.delete(this.modalURLParam);
//         window.history.pushState({}, '', url);
//         this.setModalDisplay();
//     }

//     setModalDisplay() {
//         const showModal = getModalParam()
//         if (showModal !== null && showModal !== 'false') {
//             document.getElementById(this.modalID).style.display = 'block'; // Show the modal
//         } else {
//             document.getElementById(this.modalID).style.display = 'none'; // Hide the modal
//         }
//     }

//     getModalParam() {
//         return new URLSearchParams(window.location.search).get(this.modalURLParam);
//     }
// }

// // Example usage:
// const modalManager = new ModalManager('modalOpen', 'modalID', ['openButton1', 'openButton2'], ['closeButton1', 'closeButton2']);