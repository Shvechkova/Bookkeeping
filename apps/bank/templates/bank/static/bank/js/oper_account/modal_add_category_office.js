const addCategoryOperAccount = document.querySelectorAll(
  '[data-name="modal-add_category_oper_account"]'
);

if (addCategoryOperAccount) {
  addCategoryOperAccount.forEach((element) => {
    element.addEventListener("click", (event) => {
      const battonAdd = document.querySelector(".add_category_oper_account");

      let elem = element.getAttribute("data-name");
      const modalWindow = document.getElementById(elem);

      const inputNameCAtegoru = modalWindow.querySelector(
        ".modal_add_category_input"
      );
      inputNameCAtegoru.value = "";
      getCoords(event, elem);
      modal(elem, battonAdd);

      getTitleInfoCategory(modalWindow, element);
      addCategoryOperationFetch(battonAdd, element, modalWindow,elem);
      //   modalWindow.addEventListener("input", () => {
      //     validateOtherInput(elem, ".add-category");
      //   });
    });
  });
}

// заполнение тайтла инфой
function getTitleInfoCategory(modalWindow, element) {
  let elementCat = element.getAttribute("data-cat");
  // const titleNameData = element.getAttribute("modal_title_category_data")
  const titleInput = modalWindow.querySelector(".modal_title_category_data");

  titleInput.innerHTML = `"${elementCat}"`;
}

// расположенеи модалки относительно кнопки клика
function getCoords(event, elem) {
  console.log("Позиция x относительно документа", event.pageX);
  console.log("Позиция y относительно документа", event.pageY);
  const windowModal = document.getElementById(elem);
  const windowModalWrap = windowModal.querySelector(
    ".modal-wrapper-individual"
  );
  console.log(windowModalWrap);

  windowModalWrap.style.top = event.clientY - 20 + "px";
  windowModalWrap.style.left = event.clientX - 20 + "px";
  //    windowModalWrap.style.right=0 + "px"
  windowModalWrap.style.transform = "none";
}

function addCategoryOperationFetch(battonAdd, element, modalWindow,elem) {
  console.log(battonAdd);
  battonAdd.addEventListener("click", () => {
    const meta_categ = element.getAttribute("data-meta");
    const sub_categ = element.getAttribute("data-sub-cat");

    const inputNameCat = modalWindow.querySelector(
      ".modal_add_category_input"
    ).value;

    const form = new FormData();
    form.append("name", inputNameCat);
    form.append("meta_categ", meta_categ);
    form.append("sub_categ", sub_categ);
   

    let object = {};
    form.forEach((value, key) => (object[key] = value));
    const dataJson = JSON.stringify(object);
    console.log(dataJson);

    let csrfToken = getCookie("csrftoken");
    endpoint = "/operations/api/add-category-office/";
    fetch(endpoint, {
      method: "POST",
      body: dataJson,
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
    }).then((response) => {
      if (response.ok === true) {
        const windowContent = document.getElementById(elem);
        alertSuccess(windowContent);
        const timerId = setTimeout(() => {
          location.reload();
        }, 400);
      } else {
        const windowContent = document.getElementById(elem);

        alertError(windowContent);
        const timerId = setTimeout(() => {
          location.reload();
        }, 400);
      }
    });
  });
}
