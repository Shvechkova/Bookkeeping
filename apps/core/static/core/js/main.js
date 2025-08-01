preloaderModal((isLoading = false), (isLoaded = true));
// window.onload = function () {
//   document.body.classList.add("loaded_hiding");
//   window.setTimeout(function () {
//     document.body.classList.add("loaded");
//     document.body.classList.remove("loaded_hiding");
//   }, 100);
// };

// прелоадер для модалки
isLoading = false;
isLoaded = true;
function preloaderModal(isLoading, isLoaded, setTime) {
  if (isLoading == true) {
    document.body.classList.add("loaded_hiding");
    document.body.classList.remove("loaded");
    const preloader = document.querySelector(".preloader");
    preloader.style.opacity = "1";
  }
  if (isLoaded == true) {
    document.body.classList.remove("loaded_hiding");
    document.body.classList.add("loaded");
    const preloader = document.querySelector(".preloader");
    preloader.style.opacity = "0";
  }
}
//
function preloaderModalSetTime(setTime) {
  setTimeout(preloaderModal, setTime);
}

// setTimeout(preloaderModal(), 0, (isLoading = false), (isLoaded = true));
// функция отурытия закрытия модалки
function modal(elem, buttonAdd) {
  // получение тригера об изменении данных на странице
  const changeInfo = localStorage.getItem("changeInfo");

  // открытие модалки
  const modal_windows = document.getElementById(elem);
  modal_windows.classList.add("modal-active");

  const nameclose = "." + "modal_close" + "_" + elem + "";

  //  закрытие по общемц контейнеру
  let modalWrapper = document.querySelector(".modal-wrapper");
  let modalWrapperWind = document.querySelector(".modal-items");

  modal_windows.addEventListener("click", (event) => {
    let modalWrapperWind = document.querySelector(".modal-items");

    let modalSelect = modal_windows.querySelectorAll(".modal-select");
    let modalSelectWrap = modal_windows.querySelector("#modal-select");

    if (
      event.target == modal_windows &&
      event.target != modalWrapper &&
      event.isTrusted == true
    ) {
      // если есть изменения на странице перезагрузить
      if (changeInfo === "true") {
        localStorage.removeItem("changeInfo");
        location.reload();
      }
      modal_windows.classList.remove("modal-active");
      modal_windows.replaceWith(modal_windows.cloneNode(true));
    }
  });
  // закрытие по кнопке
  let modalCloseAll = document.querySelector(nameclose);
  modalCloseAll.addEventListener("click", (event) => {
    // если есть изменения на странице перезагрузить
    if (changeInfo === "true") {
      location.reload();
    }
    modal_windows.classList.remove("modal-active");
    buttonAdd.replaceWith(buttonAdd.cloneNode(true));
  });
}

// функции завершения модального окна
function alertSuccess(element) {
  const wrap = element.querySelector(".modal-items");
  // wrap.style.padding = "100px";
  // element.querySelector(".modal-items-wrap").innerHTML = "Успех";
  const wrapper = element.querySelector(".modal-items-wrap");
  wrapper.style.opacity = 0;
  const successItem = document.createElement("div");
  successItem.className = "alert";
  successItem.innerHTML = "<strong>Успешно</strong>";
  successItem.style.opacity = 0;
  wrap.append(successItem);
  successItem.style.opacity = 1;
}
function alertError(element) {
  // element.querySelector(".modal-items-wrap").innerHTML = "Неудача, повторите";
  const wrap = element.querySelector(".modal-items");
  // wrap.style.padding = "100px";
  // element.querySelector(".modal-items-wrap").innerHTML = "Успех";
  const wrapper = element.querySelector(".modal-items-wrap");
  wrapper.style.opacity = 0;
  const successItem = document.createElement("div");
  successItem.className = "alert";
  successItem.innerHTML = "<strong>Неудача, повторите</strong>";
  successItem.style.opacity = 0;
  wrap.append(successItem);
  successItem.style.opacity = 1;
}

// предупреждение что нельзя удалить
function DontDelite(element) {
  const wrap = element.querySelector(".modal-items");
  const wrapper = element.querySelector(".modal-items-wrap");
  wrapper.style.opacity = 0;
  const successItem = document.createElement("div");
  successItem.className = "alert";
  successItem.innerHTML = "<strong>нельзя удалить</strong>";
  successItem.style.opacity = 0;
  wrap.append(successItem);
  successItem.style.opacity = 1;

  const timerId = setTimeout(() => {
    successItem.remove();
    wrapper.style.opacity = 1;
  }, 1000);
}

// получение куки с срфс токен
function getCookie(name) {
  let matches = document.cookie.match(
    new RegExp(
      "(?:^|; )" +
        name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, "\\$1") +
        "=([^;]*)"
    )
  );
  return matches ? decodeURIComponent(matches[1]) : undefined;
}

// валидация без радио кнопок
function validate(elem, btn) {
  const modalWindows = document.getElementById(elem);
  const allInputModal = modalWindows.querySelectorAll(
    "input:not([type=hidden])"
  );
  const allSelectModal = modalWindows.querySelectorAll("select");
  console.log();
  const add_contract = document.querySelector(btn);
  let inputYes;
  let selectYes;
  let validateClass = false;
  allInputModal.forEach((elInput) => {
    console.log(elInput);
    if (elInput.value == "" || elInput.value == "0" || elInput.value == " ₽") {
      console.log(elInput.value);
      const c = elInput.getAttribute("data-validate");
      if (c == 0) {
        add_contract.disabled = false;
        inputYes = true;
      } else {
        add_contract.disabled = true;
        throw false;
      }
    } else {
      console.log(elInput.value);
      add_contract.disabled = false;
      inputYes = true;
    }
  });

  allSelectModal.forEach((elSelect) => {
    const elSelectChecked = elSelect.options[elSelect.selectedIndex].value;

    if (elSelectChecked == 0 || elSelectChecked == "") {
      add_contract.disabled = true;
      throw false;
    } else {
      add_contract.disabled = false;
      selectYes = true;
    }
  });

  if (selectYes || selectYes) {
    validateClass = true;
  } else {
    validateClass = false;
  }

  return validateClass;
}
// валидация когда только инпуты
function validateOtherInput(elem, btn) {
  const modalWindows = document.getElementById(elem);
  const allInputModal = modalWindows.querySelectorAll("input");
  console.log(modalWindows);

  const add_contract = document.querySelector(btn);
  console.log(add_contract);
  let inputYes;
  let selectYes;
  let validateClass = false;
  allInputModal.forEach((elInput) => {
    if (elInput.value == "") {
      const c = elInput.getAttribute("data-validate");
      if (c == 0 || elInput.value == " ₽") {
        add_contract.disabled = false;
        inputYes = true;
      } else {
        add_contract.disabled = true;

        throw false;
      }
    } else {
      add_contract.disabled = false;
      inputYes = true;
    }
  });

  if (inputYes) {
    validateClass = true;
  } else {
    validateClass = false;
  }

  return validateClass;
}

// валидация без радио кнопок для кнопки ок дающаяя сохранить форму
function validateBtn(elem, btn) {
  console.log("validateBtn");
  const modalWindows = document.getElementById(elem);

  const add_contract = document.querySelector(btn);
  const elemParent = document.querySelector(btn).parentNode;

  const allInputModal = elemParent.querySelectorAll("input");

  const allSelectModal = elemParent.querySelectorAll("select");

  let inputYes;
  let selectYes;
  let validateClass = false;

  allInputModal.forEach((elInput) => {
    console.log(allInputModal)
    if (elInput.value == "") {
      const c = elInput.getAttribute("data-validate");
      if (c == 0) {
        add_contract.disabled = false;
        inputYes = true;
      } else {
        add_contract.disabled = true;

        throw false;
      }
    } else {
      add_contract.disabled = false;
      inputYes = true;
    }
  });

  allSelectModal.forEach((elSelect) => {
    const elSelectChecked = elSelect.options[elSelect.selectedIndex].value;

    if (elSelectChecked == 0 || elSelectChecked == "") {
      add_contract.disabled = true;
      throw false;
    } else {
      add_contract.disabled = false;
      selectYes = true;
    }
  });

  if (selectYes || selectYes) {
    validateClass = true;
  } else {
    validateClass = false;
  }

  return validateClass;
}

// валидация если есть радио кнопок
function validateRadio(elem, btn, wrapOne, wrapTwo) {
  const modalWindows = document.getElementById(elem);
  const wrapOneElem = document.querySelector(wrapOne);
  const wrapTwoElem = document.querySelector(wrapTwo);
  const allInputModalOne = wrapOneElem.querySelectorAll("input[type='radio']");
  const allInputModalTwo = wrapTwoElem.querySelectorAll("input[type='radio']");

  const add_contract = document.querySelector(btn);
  console.log(add_contract);
  let inputYes;
  let inputYesTwo;
  let validateClass = false;
  allInputModalOne.forEach((elInput) => {
    if (elInput.checked == false) {
      add_contract.disabled = true;
    } else {
      add_contract.disabled = false;
      inputYes = true;
    }
  });

  allInputModalTwo.forEach((elInput) => {
    if (elInput.checked == false) {
      add_contract.disabled = true;
    } else {
      add_contract.disabled = false;
      inputYesTwo = true;
    }
  });
  if (inputYes && inputYesTwo) {
    validateClass = true;
    add_contract.disabled = false;
  } else {
    validateClass = false;
    add_contract.disabled = true;
  }
  console.log(validateClass);
  return validateClass;
}

// класс конструктор инпутов
class Input {
  constructor(type, className, value, placeholder, readonly, dataname) {
    this.elem = document.createElement("input");
    if (type) this.elem.type = type;
    if (className) this.elem.className = className;
    if (value) this.elem.value = value;
    if (placeholder) this.elem.placeholder = placeholder;
    if (readonly == true) this.elem.readOnly = true;
    if (dataname) this.elem.setAttribute("data-id", dataname);
  }

  appendTo(parent) {
    parent.append(this.elem);
  }

  afterTo(parent) {
    parent.after(this.elem);
  }
}
// класс конструктор оптион в селектах
class selectOption {
  constructor(className, value, id, text, selected, disabled) {
    this.elem = document.createElement("option");
    if (className) this.elem.className = className;
    if (value) this.elem.value = value;
    if (id) this.elem.setAttribute("data-id", id);
    if (text) this.elem.innerHTML = text;
    if (selected == id) this.elem.selected = true;
    if (disabled == true) this.elem.disabled = true;
  }

  appendTo(parent) {
    parent.append(this.elem);
  }
}
// смена цвета оптион на серый
function choiceColor() {
  let choice = document.querySelectorAll(".choice");
  choice.forEach((element) => {
    const selectedValue = element.value;
    if (element.value == 0) {
      element.classList.add("empty");
    } else element.classList.remove("empty");

    element.addEventListener("change", (event) => {
      if (element.value == 0) {
        element.classList.add("empty");
      } else element.classList.remove("empty");
    });
  });
}

// чекин окна другой сумы

function ChekinOtherSum(inputOtherSum, radioOtherSum) {
  const chekinOtherSum = document.getElementById(inputOtherSum);
  if (chekinOtherSum) {
    chekinOtherSum.addEventListener("input", () => {
      const chekinOtherSum = document.getElementById(radioOtherSum);
      if (chekinOtherSum) {
        chekinOtherSum.checked = true;
      }
    });
  }
}

// добавление знаков рубля в инпуты с суммами
function replaceNam() {
  // const sel = document.querySelectorAll(".pyb");
  // sel.forEach((elem) => {
  //   if (elem.value != "") {
  //     elem.value =
  //       elem.value
  //         .replace(/\d $ /, "")
  //         .replace(/\D/g, "")
  //         .replace(/(\d)(?=(\d{3})+([^\d]|$))/g, "$1 ") + " ₽";
  //   }
  //   elem.addEventListener("keydown", (event) => {
  //     var key = event.keyCode;
  //     if (key != 8) {
  //       // elem.value =
  //       //   elem.value
  //       //     .replace(/\d $ / , "")
  //       //     .replace(/\D/g, "")
  //       //     .replace(/(\d)(?=(\d{3})+([^\d]|$))/g, "$1 ") + " ₽";
  //       // if (elem.value == " ₽") {
  //       //   elem.value = "";
  //       // }
  //     } else {
  //       var s = elem.value;
  //       elem.setSelectionRange(s.length - 2, s.length - 2);
  //       if (elem.value == " ₽") {
  //         elem.value = null
  //       }
  //     }
  //   });
  // });
}

function replaceNamDot() {
  // const sel = document.querySelectorAll(".pyb");
  // sel.forEach((elem) => {
  //   if (elem.value != "") {
  //     elem.value =
  //       elem.value
  //         .replace(/\d $ /, "")
  //         .replace(/\D/g, "")
  //         .replace(/(\d)(?=(\d{3})+([^\d]|$))/g, "$1 ") + " ₽";
  //   }

  //   elem.addEventListener("input", () => {
  //     elem.value =
  //       elem.value
  //         .replace(/\d $ /, "")
  //         .replace(/\D/g, "")
  //         .replace(/(\d)(?=(\d{3})+([^\d]|$))/g, "$1 ") + " ₽";

  //     if (elem.value == " ₽") {
  //       elem.value = "";
  //     }
  //   });
  // });
}
function getCurrentPrice(p) {
  console.log("p",p)
  p = String(p)
  let price = p.replace(",", ".").replace(/(\d)\++/g, "$1").replace(/\s/g, '')
  // price = p.replaceAll(" ", '');
  console.log("price",price)
  price = Number(price);
  console.log("getCurrentPriceprice",price)
  return price;
}
function getCurrentPriceJS(p) {
  console.log("getCurrentPriceJS(p)", p);
  let price = p.replace(",", ".").replace(/(\d)\++/g, "$1").replace(/\s/g, '');
  price = Number(price);
  return price;
}
function monthToInt(str) {
  if (str == "Январь") return "01";
  if (str == "Февраль") return "02";
  if (str == "Март") return "03";
  if (str == "Апрель") return "04";
  if (str == "Май") return "05";
  if (str == "Июнь") return "06";
  if (str == "Июль") return "07";
  if (str == "Август") return "08";
  if (str == "Сентябрь") return "09";
  if (str == "Октябрь") return "10";
  if (str == "Ноябрь") return "11";
  if (str == "Декабрь") return "12";
  return 0;
}

// document.addEventListener('DOMContentLoaded', _ => {
//   const elems = document.querySelectorAll('.invoice_month_out_additional')
//   if (elems) {
//     console.log("elems", elems)
//     elems.forEach((elementItem, i) => {
//       const dataShrinkDateItem = elementItem.getAttribute("data-attr-shrink-item");
//       console.log("dataShrinkDateItem", dataShrinkDateItem)
//       if (localStorage.getItem(dataShrinkDateItem)) {
//         elementItem.style.display = 'none';
//         const btnShr = document.querySelector(`[data-attr-shrink=${dataShrinkDateItem}]`)
//         btnShr.style.transform = 'rotate(' + 180 + 'deg)';
//         // localStorage.setItem(dataShrinkDateItem, 0)
//       }
//     })

//     // if (localStorage.getItem('elem'))

//     const btn = document.querySelectorAll('.btn_month_invoce-shrink')
//     btn.forEach((element, i) => {
//       element.addEventListener("click", () => {
//         const dataShrinkDate = element.getAttribute("data-attr-shrink");
//         console.log(dataShrinkDate)
//         const shrinkElem = document.querySelectorAll(`.${dataShrinkDate}`)
//         if (localStorage.getItem(dataShrinkDate)) {
//           console.log(99999)
//           shrinkElem.forEach((elementSr, i) => {
//             elementSr.style.display = 'block';
//           })
//           localStorage.removeItem(dataShrinkDate)
//           element.style.transform = 'rotate(' + 0 + 'deg)';

//         } else {
//           shrinkElem.forEach((elementSr, i) => {
//             elementSr.style.display = 'none';
//           })
//           localStorage.setItem(dataShrinkDate, 1)
//           element.style.transform = 'rotate(' + 180 + 'deg)';
//         }

//       })

//     })
//   }
//   // if (localStorage.getItem('elem')) elem.disabled = true;
//   // const btn = document.querySelector('.btn_month_invoce-shrink')
//   // console.log(btn)
//   // btn.addEventListener("click", function() {
//   //   elem.disabled = true;
//   //   localStorage.setItem('elem', 1)
//   // })
// })
function ShrinkHorizon2() {
  
    const elems = document.querySelectorAll(".shrink-item");
    if (elems) {
      console.log("elems", elems);
      elems.forEach((elementItem, i) => {
        const dataShrinkDateItem = elementItem.getAttribute(
          "data-attr-shrink-name"
        );
        console.log("dataShrinkDateItem", dataShrinkDateItem);
        if (localStorage.getItem(dataShrinkDateItem)) {
          const shrinkElem = document.querySelectorAll(
            `.${dataShrinkDateItem}`
          );
          shrinkElem.forEach((elementSr, i) => {
            elementSr.style.display = "none";
            const btnShr = document.querySelector(
              `[data-attr-shrink=${dataShrinkDateItem}]`
            );
            btnShr.style.transform = "rotate(" + 180 + "deg)";
            elementSr.style.background = "none";
            // ShrinkVert()
            // localStorage.setItem(dataShrinkDateItem, 0)
          });
        }
      });
    }
 
}
function ShrinkVert() {
  document.addEventListener("DOMContentLoaded", (_) => {
    const elems = document.querySelectorAll(".shrink-item-vert");
    if (elems) {
      elems.forEach((elementItem, i) => {
        const dataShrinkDateItem = elementItem.getAttribute(
          "data-attr-shrink-name-vert"
        );
        console.log("dataShrinkDateItem", dataShrinkDateItem);
        if (localStorage.getItem(dataShrinkDateItem)) {
          const shrinkElem = document.querySelectorAll(
            `.${dataShrinkDateItem}`
          );
          shrinkElem.forEach((elementSr, i) => {
            elementSr.style.display = "none";
            const btnShr = document.querySelector(
              `[data-attr-shrink-vert=${dataShrinkDateItem}]`
            );
            btnShr.style.transform = "rotate(" + 180 + "deg)";
            elementSr.style.background = "none";
            // localStorage.setItem(dataShrinkDateItem, 0)
          });
        }
      });

      const btn = document.querySelectorAll(".shrink-item-vert");
      btn.forEach((element, i) => {
        element.addEventListener("click", () => {
          const dataShrinkDate = element.getAttribute(
            "data-attr-shrink-name-vert"
          );
          console.log("dataShrinkDate", dataShrinkDate);
          const shrinkElem = document.querySelectorAll(`.${dataShrinkDate}`);
          if (localStorage.getItem(dataShrinkDate)) {
            console.log(99999);
            console.log(shrinkElem);
            const page = document.querySelector("#page_name");
            let display = "block";
            if (page || page.value == "salary") {
              display = "flex";
            }
            console.log(display);
            shrinkElem.forEach((elementSr, i) => {
              elementSr.style.display = display;
            });
            localStorage.removeItem(dataShrinkDate);
            element.style.transform = "rotate(" + 0 + "deg)";
            ShrinkHorizon2()
          } else {
            shrinkElem.forEach((elementSr, i) => {
              elementSr.style.display = "none";
            });
            localStorage.setItem(dataShrinkDate, 1);
            element.style.transform = "rotate(" + 180 + "deg)";
            ShrinkHorizon2()
          }
        });
      });
    }
  });
}
ShrinkVert();

function ShrinkVert2() {
  const elems = document.querySelectorAll(".shrink-item-vert");
  if (elems) {
    elems.forEach((elementItem, i) => {
      const dataShrinkDateItem = elementItem.getAttribute(
        "data-attr-shrink-name-vert"
      );
      console.log("dataShrinkDateItem", dataShrinkDateItem);
      if (localStorage.getItem(dataShrinkDateItem)) {
        const shrinkElem = document.querySelectorAll(`.${dataShrinkDateItem}`);
        shrinkElem.forEach((elementSr, i) => {
          elementSr.style.display = "none";
          const btnShr = document.querySelector(
            `[data-attr-shrink-vert=${dataShrinkDateItem}]`
          );
          btnShr.style.transform = "rotate(" + 180 + "deg)";
          elementSr.style.background = "none";
          // localStorage.setItem(dataShrinkDateItem, 0)
        });
      }
    });
  }
}

function ShrinkHorizon() {
  document.addEventListener("DOMContentLoaded", (_) => {
    const elems = document.querySelectorAll(".shrink-item");
    if (elems) {
      console.log("elems", elems);
      elems.forEach((elementItem, i) => {
        const dataShrinkDateItem = elementItem.getAttribute(
          "data-attr-shrink-name"
        );
        console.log("dataShrinkDateItem", dataShrinkDateItem);
        if (localStorage.getItem(dataShrinkDateItem)) {
          const shrinkElem = document.querySelectorAll(
            `.${dataShrinkDateItem}`
          );
          
          ShrinkMoreElem(elementItem,false)
          shrinkElem.forEach((elementSr, i) => {
            
            elementSr.style.display = "none";
            const btnShr = document.querySelector(
              `[data-attr-shrink=${dataShrinkDateItem}]`
            );
            btnShr.style.transform = "rotate(" + 180 + "deg)";
            elementSr.style.background = "none";
            // ShrinkVert()
            // localStorage.setItem(dataShrinkDateItem, 0)
          });
        } else{
          ShrinkMoreElem(elementItem,true)
        }
      });

      const btn = document.querySelectorAll(".shrink-item");
      btn.forEach((element, i) => {
        element.addEventListener("click", () => {
          ShrinkMoreElem(element)

          const dataShrinkDate = element.getAttribute("data-attr-shrink-name");
          console.log("dataShrinkDate", dataShrinkDate);
          const shrinkElem = document.querySelectorAll(`.${dataShrinkDate}`);
          if (localStorage.getItem(dataShrinkDate)) {
            ShrinkMoreElem(element,true)
            const page = document.querySelector("#page_name");
            let display = "block";
            if (page & page.value == "salary") {
              display = "flex";
            }
            shrinkElem.forEach((elementSr, i) => {
              elementSr.style.display = display;
            });
            localStorage.removeItem(dataShrinkDate);
            element.style.transform = "rotate(" + 0 + "deg)";
            ShrinkVert2();
          } else {
            ShrinkMoreElem(element,false)
            shrinkElem.forEach((elementSr, i) => {
              elementSr.style.display = "none";
            });
            localStorage.setItem(dataShrinkDate, 1);
            element.style.transform = "rotate(" + 180 + "deg)";
            ShrinkVert2();
          }
        });
      });
    }
    // if (localStorage.getItem('elem')) elem.disabled = true;
    // const btn = document.querySelector('.btn_month_invoce-shrink')
    // console.log(btn)
    // btn.addEventListener("click", function() {
    //   elem.disabled = true;
    //   localStorage.setItem('elem', 1)
    // })
  });
}
ShrinkHorizon();


function ShrinkMoreElem(elementItem,is_none){
  console.log("elementItem",elementItem)
  const shrinkItemMore = elementItem.getAttribute(
    "data-attr-shrink-item-more"
  );
  console.log("shrinkItemMore",shrinkItemMore)
  if (shrinkItemMore){
    elementItem.setAttribute("data-attr-shrink-item-more-tag", is_none);
    const allElemAttr = document.querySelectorAll(`[data-attr-shrink-item-more=${shrinkItemMore}]`);
    // Проверка наличия data-атрибута
    let toElement = null;
    if (elementItem.hasAttribute('data-attr-shrink-item-to-element')) {
      console.log('data-id существует');
      toElement = elementItem.getAttribute("data-attr-shrink-item-to-element");
      elementItemDop = elementItem.parentElement.parentElement.querySelector(".outside_wr_mini")
      console.log("elementItemDop",elementItemDop)
      
    }
    // Проверяем все элементы на наличие атрибута data-attr-shrink-item-more-tag = false
    const allElementsHaveFalseTag = Array.from(allElemAttr).every(elem => 
      elem.getAttribute("data-attr-shrink-item-more-tag") === "false"
    );
    
    if (allElementsHaveFalseTag) {
      console.log("Все элементы имеют data-attr-shrink-item-more-tag = false");
      all_elem = document.querySelectorAll(
        `[data-attr-shrink-item-more-last=${shrinkItemMore}]`
      );
      console.log(`[data-attr-shrink-item-more-last=${shrinkItemMore}]`)
      all_elem.forEach(elem => {
        elem.style.display = "none";
      });
      if (elementItem.hasAttribute('data-attr-shrink-item-to-element')) {
        console.log('data-id существует');
        toElement = elementItem.getAttribute("data-attr-shrink-item-to-element");
        elementItemDop = elementItem.parentElement.parentElement.querySelector(".outside_wr_mini")
        console.log("elementItemDop",elementItemDop)
        elementItemDop.style.display = "block";
      }
    }else{
      all_elem = document.querySelectorAll(
        `[data-attr-shrink-item-more-last=${shrinkItemMore}]`
      );

      all_elem.forEach(elem => {
        elem.style.display = "block";
      });
      if (elementItem.hasAttribute('data-attr-shrink-item-to-element')) {
        console.log('data-id существует');
        toElement = elementItem.getAttribute("data-attr-shrink-item-to-element");
        elementItemDop = elementItem.parentElement.parentElement.querySelector(".outside_wr_mini")
        console.log("elementItemDop",elementItemDop)
        elementItemDop.style.display = "none";
      }
    }
    
    // console.log("shrinkItemMore",shrinkItemMore)
    // all_elem = document.querySelectorAll(
    //   `[data-attr-shrink-item-more-last=${shrinkItemMore}]`
    // )
    // console.log("all_elem",all_elem)
  }else{
    console.log("NONE")
  }
}
  