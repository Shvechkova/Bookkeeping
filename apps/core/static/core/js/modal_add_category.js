const addCategory = document.querySelector('[data-name="modal-add-category"]');
if (addCategory) {
    addCategory.addEventListener("click", () => {
        const battonAdd = document.querySelector(
            ".add-category"
          );
       
        let elem = addCategory.getAttribute("data-name");
        const modalWindow = document.getElementById(elem)
        const inputNameCAtegoru = modalWindow.querySelector(".modal_add_category_input")
        inputNameCAtegoru.value = ""
        modal(elem, battonAdd);
        getTitleInfoCategory(addCategory,modalWindow)

        modalWindow.addEventListener("input", () => {
            
            validateOtherInput(elem, ".add-category");
          });
    })
}

// заполнение тайтла инфой
function getTitleInfoCategory(element,modalWindow){
    let elementCat = element.getAttribute("data-cat");
    // const titleNameData = element.getAttribute("modal_title_category_data")
    const titleInput = modalWindow.querySelector(".modal_title_category_data")
   
    titleInput.innerHTML = elementCat

}