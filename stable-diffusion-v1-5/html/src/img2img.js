/*
File: img2img.js
Author: Chuncheng Zhang
Date: 2023-04-18
Copyright & Email: chuncheng.zhang@ia.ac.cn

Functions:
    1. Pending
    2. Pending
    3. Pending
    4. Pending
    5. Pending
*/

// %% ---- 2023-04-18 ------------------------
// Pending
{
  var { clearPromptButton, promptTextarea } = getImg2imgElements();
  clearPromptButton.onclick = () => {
    promptTextarea.value = "";
  };
}

// %% ---- 2023-04-18 ------------------------
// Pending
setImg2imgMainImg(Global.exchangeImgPath);

// %% ---- 2023-04-18 ------------------------
// Pending
function setImg2imgMainImg(src) {
  var { statusBar, mainImg } = getImg2imgElements();
  mainImg.src = src ? src : Global.exchangeImgPath;
  statusBar.innerHTML = `
          Image request:   <span class='text-success'>${mainImg.src}</span>
          `;

  mainImg.onload = () => {
    console.log("The main image is loaded", src);
  };
}

// %% ---- 2023-04-18 ------------------------
// Pending
getImg2imgElements().submitPromptButton.onclick = () => {
  var { prompt, statusBar, mainImg, candidatesGallery } = getImg2imgElements();

  pendingImg2img(statusBar, prompt);

  // Request the operation
  var url = new URL(mainImg.src);

  d3.json(
    "operation/img2img?prompt=" +
      prompt +
      "&initImg=" +
      url.searchParams.get("path")
  ).then((imgPathList) => {
    // Reset the main img
    mainImg.style.filter = "";

    // Draw the main img with the 1st images from the backend.
    var src = "request/img?path=" + imgPathList[0];
    setImg2imgMainImg(src, prompt);

    // Clear the candidates gallery
    candidatesGallery.innerHTML = "";

    // Fill the candidates gallery with the images,
    // and add the click event to the gallery,
    // it replaces the main img with the clicked images.
    d3.select(candidatesGallery)
      .selectAll("img")
      .data(imgPathList)
      .enter()
      .append("img")
      .attr("src", (d) => `request/img?path=${d}`)
      .attr("class", "img-fluid img-thumbnail")
      .attr("alt", "img-alt")
      .on("click", (e, d) => {
        console.log(e, d);
        var src = `request/img?path=${d}`;
        setImg2imgMainImg(src, prompt);
      });
  });
};

// %% ---- 2023-04-18 ------------------------
/**
 * Setup statusBar to the pending status.
 *
 * @param {Elem} statusBar The status bar to be updated with
 * @param {String} prompt The prompt to be inserted in the status bar
 */
function pendingImg2img(statusBar, prompt) {
  // Report the pending status.
  statusBar.innerHTML = `
      <span class="placeholder">... 
      <span class='text-danger'>Pending with prompt...</span>
      </span>
      <span class='text-danger'>${prompt}</span>
      `;
  console.log("Submit prompt:", prompt);
}

// %% ---- 2023-04-18 ------------------------
// Pending
/**
 * Get the current values and elements of the img2img session.
 *
 * @returns Object with the current values and elements
 */
function getImg2imgElements() {
  var _ = 0,
    // Main section
    mainSection = document.getElementById("img2img-section"),
    // Prompt
    promptTextarea = document.getElementById("img2img-prompt-textarea"),
    { value: prompt } = promptTextarea,
    // Statusbar
    statusBar = document.getElementById("img2img-status-bar"),
    // Main image
    mainImg = document.getElementById("img2img-main-img"),
    // The container of the candidates imgs
    candidatesGallery = document.getElementById(
      "img2img-thumbnail-imgs-container"
    ),
    // Buttons
    submitPromptButton = document.getElementById(
      "img2img-button-submit-prompt"
    ),
    clearPromptButton = document.getElementById("img2img-button-clear-prompt"),
    __ = 0;

  return {
    mainSection,
    promptTextarea,
    prompt,
    statusBar,
    mainImg,
    candidatesGallery,
    submitPromptButton,
    clearPromptButton,
  };
}
