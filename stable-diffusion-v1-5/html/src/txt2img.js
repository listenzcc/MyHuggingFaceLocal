/*
File: txt2img.js
Author: Chuncheng Zhang
Date: 2023-04-17
Copyright & Email: chuncheng.zhang@ia.ac.cn

Functions:
    1. Functions for the txt2img section
    2. Pending
    3. Pending
    4. Pending
    5. Pending
*/

// %% ---- 2023-04-17 ------------------------
// Functions for the txt2img section

// Handler of the clear button
{
  var { clearPromptButton, promptTextarea, refreshHistoryButton } =
    getTxt2imgElements();
  clearPromptButton.onclick = () => {
    promptTextarea.value = "";
  };

  refreshHistoryButton.onclick = () => {
    refreshHistorySelector();
  };
  refreshHistorySelector();
}

// %% ---- 2023-04-17 ------------------------
/**
 * Refresh the history selector
 */
function refreshHistorySelector() {
  d3.json("request/txt2img/history").then((history) => {
    var select = document.getElementById("txt2img-history-select");
    select.innerHTML = "";

    d3.select("#txt2img-history-select")
      .selectAll("option")
      .data(history)
      .enter()
      .append("option")
      .text((d) => d.folder);

    select.oninput = () => {
      selectOninput();
    };

    // Call the selectOninput, since the options are updated.
    selectOninput();

    /**
     * Oninput handler of the select
     */
    function selectOninput() {
      // Stage 1, setups.
      var selectHistory = history.filter((d) => d.folder === select.value)[0],
        { images: imgPathList, setup } = selectHistory,
        { prompt } = setup,
        { promptTextarea, statusBar, mainImg, candidatesGallery } =
          getTxt2imgElements();

      console.log("Select history record:", selectHistory, imgPathList);
      promptTextarea.value = prompt;

      // Stage 2, operation in the backend.
      pendingTxt2img(statusBar, mainImg, prompt);

      {
        // Reset the main img
        mainImg.style.filter = "";

        // Draw the main img with the 1st images from the backend.
        var src = "request/img?path=" + imgPathList[0];
        setTxt2imgMainImg(src, prompt);

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
            setTxt2imgMainImg(src, prompt);
          });
      }
    }
  });
}

// Submit button
getTxt2imgElements().submitPromptButton.onclick = () => {
  // Stage 1, setups.
  var { prompt, statusBar, mainImg, candidatesGallery } = getTxt2imgElements();

  // Stage 2, operation in the backend.
  pendingTxt2img(statusBar, mainImg, prompt);

  // Request the operation
  d3.json("operation/txt2img?prompt=" + prompt).then((imgPathList) => {
    // Reset the main img
    mainImg.style.filter = "";

    // Draw the main img with the 1st images from the backend.
    var src = "request/img?path=" + imgPathList[0];
    setTxt2imgMainImg(src, prompt);

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
        setTxt2imgMainImg(src, prompt);
      });
  });
};

// %% ---- 2023-04-17 ------------------------
// Pending

// %% ---- 2023-04-17 ------------------------
// Pending

/**
 * Setup statusBar and mainImg to the pending status.
 *
 * @param {Elem} statusBar The status bar to be updated with
 * @param {Element} mainImg The image to be blurred
 * @param {String} prompt The prompt to be inserted in the status bar
 */
function pendingTxt2img(statusBar, mainImg, prompt) {
  // Report the pending status.
  statusBar.innerHTML = `
      <span class="placeholder">... 
      <span class='text-danger'>Pending with prompt...</span>
      </span>
      <span class='text-danger'>${prompt}</span>
      `;
  console.log("Submit prompt:", prompt);

  // Blur the main img, showing it will be replaced.
  mainImg.style.filter = "blur(5px)";
}

// %% ---- 2023-04-17 ------------------------
/**
 * Set the image to the mainImage element,
 * and set the statusBar accordingly.
 *
 * @param {string} src The src of the image.
 * @param {string} prompt The prompt of the image.
 */
function setTxt2imgMainImg(src, prompt) {
  var { statusBar, mainImg } = getTxt2imgElements();
  mainImg.src = src;
  statusBar.innerHTML = `
          Image prompt: <span class='text-primary'>${prompt}</span>,<br />
          Image request:   <span class='text-success'>${src}</span>
          `;

  mainImg.onload = () => {
    console.log("The main image is loaded", src, prompt);
  };

  Global.exchangeImgPath = src;
  console.log("Set the exchangeImgPath with", src);
}

// %% ---- 2023-04-17 ------------------------
/**
 * Get the current values and elements of the txt2img session.
 *
 * @returns Object with the current values and elements
 */
function getTxt2imgElements() {
  var _ = 0,
    // Main section
    mainSection = document.getElementById("txt2img-section"),
    // Prompt
    promptTextarea = document.getElementById("txt2img-prompt-textarea"),
    { value: prompt } = promptTextarea,
    // The status bar
    statusBar = document.getElementById("txt2img-status-bar"),
    // The main img
    mainImg = document.getElementById("txt2img-main-img"),
    // The container of the candidates imgs
    candidatesGallery = document.getElementById(
      "txt2img-thumbnail-imgs-container"
    ),
    // Buttons
    submitPromptButton = document.getElementById(
      "txt2img-button-submit-prompt"
    ),
    clearPromptButton = document.getElementById("txt2img-button-clear-prompt"),
    refreshHistoryButton = document.getElementById(
      "txt2img-button-refresh-history"
    ),
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
    refreshHistoryButton,
  };
}
