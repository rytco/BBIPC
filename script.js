const overlayImage = document.getElementById('overimg');
const overlayButton = document.getElementById('Overlayb');

overlayButton.addEventListener('click', () => {
    overlayImage.style.opacity = overlayImage.style.opacity === '1' ? '0' : '1';
   
})

