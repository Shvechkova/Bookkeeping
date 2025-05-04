choiceColor();

const btnSubcontarct = document.querySelectorAll(".add_sabcontactor");

if (btnSubcontarct) {
  btnSubcontarct.forEach((element) => {
    element.addEventListener("click", () => {
      let elem = element.getAttribute("data-name");
      let idBill = element.getAttribute("data-bill-month-id");
      let sumAdv = element.getAttribute("data-bill-month-adv");
      let typeSuborder = element.getAttribute("data-type-suborder");

      const title = document.querySelector("#page_name").value;
      if (title == "1") {
        // замена использованныых бюджетов если адв
        let useBudget = document.querySelector(".modal_adv_budget_not_use");
        let useBudgetAfterUse = document.getElementById("sum_adv_after_use");
        useBudgetAfterUse.value = "";
        useBudget.innerHTML = "";
        const slash = document.querySelector(".modal_adv_budget_not_use_slash");
        slash.style.display = "none";
        // вставка бюджета
        let budgetInnerAll = document.querySelector(".modal_adv_budget_all");

        budgetInnerAll.innerHTML = sumAdv + "  ₽";
      }

      // открытие модалки
      const add_subc = document.querySelector(".subcontarct_add");
      modal(elem, add_subc);
      // окно для адв или остальных изменение тйтла
      if (typeSuborder == "awords") {
        const modalWindow = document.getElementById(elem);
        const buget = modalWindow.querySelector(".modal_adv_buget");
        buget.innerHTML =
          "<div class='modal_adv_buget'><h3>Субподряд и премии:</h3></div>";
      }
      // очистка от загруженных субконтрактов
      const c = document.querySelector(".modal_add_subcontract_wrapper");
      // c.innerHTML = ""
      c.innerHTML =
        '<div class="modal_add_contract modal_add-subcontract"><select class="modal-subcontract-type choice"><option disabled selected class="modal-select empty" value="0">Тип</option><option class="modal-select" value="adv">площадка</option><option class="modal-select" value="other">премия</option></select></div>';

      // основные функции
      getOldSumcintract(idBill, element, elem);
      getInfoBill(element);
      createInputSubcontract(element, elem);

      addSubcontractFetch(idBill, elem);

      observerChangeCreateInput(element, elem);
      // валидация
      const modalWindows = document.getElementById(elem);
      modalWindows.addEventListener("input", () => {
        replaceNam();
        validate(elem, ".modal_add_subcontract");
      });
      modalWindows.addEventListener("input", () => {
        validateBtn(elem, ".subcontarct_add");
      });
    });
  });
}
// функции заполнения тайтлов инфой о контракте
function getInfoBill(element) {
  const clientName = element.getAttribute("data-bill-month-client-name");
  const contractName = element.getAttribute("data-bill-month-name");
  const contractData = element.getAttribute("data-bill-month-data");
  const advMonthSum = element.getAttribute("data-bill-month-adv");

  const modalClient = document.querySelector(".add-subcontract_client-name");
  const modalContract = document.querySelector(
    ".add-subcontract_contract-name"
  );
  const modalData = document.querySelector(".add-subcontract_data");

  modalClient.innerHTML = clientName;
  modalContract.innerHTML = contractName;
  modalData.innerHTML = contractData;
  const title = document.querySelector("#page_name").value;
  if (title == "1") {
    const slash = document.querySelector(".modal_adv_budget_not_use_slash");
    slash.style.display = "block";
    console.log(advMonthSum);
    let useBudgetAfterUse = document.querySelector(".modal_adv_budget_not_use");
    console.log(useBudgetAfterUse);
    useBudgetAfterUse.innerHTML = advMonthSum;
  }
}
// создание инпутов для заполнение субконтракта fetch категорий
function createInputSubcontract(element, elem) {
  const subTypeSelect = document.querySelectorAll(".modal-subcontract-type");
  subTypeSelect.forEach((el) => {
    el.addEventListener("change", (event) => {
      if (el.nextSibling) {
        while (el.parentNode.children.length > 1) {
          el.parentNode.removeChild(el.parentNode.lastChild);
        }
      }
      let subcontractCategory = el.value;
      let endpoint = "/api/v1/adv-platform/" + subcontractCategory + "/";
      // let endpoint =
      //   "/service/api/subcontract-category
      fetch(endpoint, {
        method: "get",
      })
        .then((response) => response.json())
        .then((data) => {
          let select = document.createElement("select");
          select.className = "modal-subcontract-type_choises choice";
          el.after(select);
          data.forEach(function (value, key) {
            new selectOption(
              "modal-select input-130",
              value.id,
              value.id,
              value.name
            ).appendTo(select);
          });
          new Input(
            "text",
            "modal-subcontract-input_sum input-200 num_budet pyb",
            "",
            "сумма"
          ).afterTo(select);

          let button = document.createElement("button");
          button.className = "modal_add_subcontract";
          button.innerHTML = "OK";
          button.disabled = true;
          select.nextElementSibling.after(button);

          new Input("hidden", "subcontract_id", "0").afterTo(select);
          const buttonAdd = document.querySelector(".subcontarct_add");
          buttonAdd.disabled = true;
          button.innerHTML = "OK";

          // let hhh = document.createElement("span");
          // hhh.className = "spn";
          // hhh.innerHTML = "₽";
          // button.after(hhh);

          createNextSubcontractInput(button, elem);
          replaceNam();
          return;
        });
    });
  });
}
// добавление инпутов после клика по ок
function createNextSubcontractInput(button, elem) {
  button.addEventListener("click", () => {
    let wrapperSubcontractInp = button.parentNode;
    var throwawayNode = wrapperSubcontractInp.removeChild(button);
    let dupNode = wrapperSubcontractInp.cloneNode();
    let dupSelect = wrapperSubcontractInp.firstElementChild.cloneNode(true);

    wrapperSubcontractInp.after(dupNode);
    dupNode.append(dupSelect);
    createInputSubcontract();
  });
}
// обсчет выводимой в татле сумме распред не распред субподряда
function changeSum(element, elem) {
  const title = document.querySelector("#page_name").value;
  if (title == "1") {
    let sumAdv = element.getAttribute("data-bill-month-adv");

    let sumAdvReplace = sumAdv.replace(/\s+/g, "");

    const wrapSubcontractors = document.querySelectorAll(
      ".modal-subcontract-input_sum"
    );
    let useBudget = document.querySelector(".modal_adv_budget_not_use");
    let useBudgetAfterUse = document.getElementById("sum_adv_after_use");
    var sum = sumAdvReplace;
    let useBudgetAfterUseIn = useBudgetAfterUse.value;

    const modalWindow = document.getElementById(elem);

    // wrapSubcontractors.forEach((el, value) => {
    //   el.addEventListener("keyup", () => {

    //     const slash = document.querySelector(".modal_adv_budget_not_use_slash");
    //     slash.style.display = "block";

    //     if (useBudgetAfterUseIn >= 0 && useBudgetAfterUseIn != "") {

    //       if (el.value == "" || el.value == " ₽") {
    //         intEl = 0;
    //       } else {
    //         intEl = parseInt(
    //           el.value.replace(/[^+\d]/g, "").replace(/(\d)\++/g, "$1")
    //         );
    //       }

    //       let useBudgetAfterUseInit = parseInt(
    //         useBudgetAfterUseIn.replace(/[^+\d]/g, "").replace(/(\d)\++/g, "$1")
    //       );

    //       sum = useBudgetAfterUseInit - intEl;
    //       var num = +sum;
    //       var result = num.toLocaleString();

    //       useBudget.innerHTML = result + " ₽";
    //       useBudgetAfterUse.value = sum;
    //     } else {
    //       let intEl;
    //       if (el.value == "") {
    //         intEl = 0;
    //       } else {
    //         intEl = parseInt(
    //           el.value.replace(/[^+\d]/g, "").replace(/(\d)\++/g, "$1")
    //         );
    //       }
    //       sum = sumAdvReplace - intEl;

    //       var num = +sum;
    //       var result = num.toLocaleString();

    //       useBudget.innerHTML = result + " ₽";
    //       useBudgetAfterUse.value = sum;
    //     }
    //   });
    // });

    modalWindow.addEventListener("keyup", () => {
      let sumKeyup = 0;

      wrapSubcontractors.forEach((el) => {
        const slash = document.querySelector(".modal_adv_budget_not_use_slash");
        slash.style.display = "block";

        if (el.value == "" || el.value == " ₽") {
          intEl = 0;
        } else {
          intEl = parseInt(
            el.value.replace(/[^+\d]/g, "").replace(/(\d)\++/g, "$1")
          );
        }

        let useBudgetAfterUseInit = parseInt(
          useBudgetAfterUseIn.replace(/[^+\d]/g, "").replace(/(\d)\++/g, "$1")
        );

        sum = sumAdvReplace - intEl;
        sumKeyup += intEl;
        sum = sumAdvReplace - sumKeyup;
        var result = sum.toLocaleString();
        useBudget.innerHTML = result + " ₽";
        useBudgetAfterUse.value = sum;
      });
    });
  }
}

// обсервер отслеживатель
function observerChangeCreateInput(element, elem) {
  const wrapSubcontractors = document.querySelector(
    ".modal_add_subcontract_wrapper"
  );

  let observer = new MutationObserver((mutationRecords) => {
    changeSum(element, elem);
  });
  observer.observe(wrapSubcontractors, {
    childList: true, // наблюдать за непосредственными детьми
    subtree: true, // и более глубокими потомками
    // characterDataOldValue: true // передавать старое значение в колбэк
  });
}
// отправка субконтрактов
function addSubcontractFetch(idBill, elem) {
  const buttonAddSubcontract = document.querySelector(".subcontarct_add ");
  buttonAddSubcontract.addEventListener("click", () => {
    const subcontractArr = document.querySelectorAll(".modal_add-subcontract ");
    let arrSubcontarctAll = [];
    let contractId;

    subcontractArr.forEach((element, i) => {
      contractChild = element.children;
      const nameSubcontract = contractChild[1];
      let subcontractAdv;
      let subcontractOther;
      let idelemOld = contractChild[3];

      if (idelemOld === undefined) {
      } else {
        if (idelemOld.classList.contains("subcontract_id")) {
          let namesubs = contractChild[0].getAttribute("placeholder");
          choseNameSubcontract = nameSubcontract.getAttribute("data-id");
          if (namesubs == "adv") {
            subcontractAdv = choseNameSubcontract;
            subcontractOther = null;
          } else {
            subcontractOther = choseNameSubcontract;
            subcontractAdv = null;
          }
          let amount = contractChild[2].value
            .replace(/[^+\d]/g, "")
            .replace(/(\d)\++/g, "$1");

          const contractObj = {
            id: idelemOld.value,
            month_bill: idBill,
            amount: amount,
            platform: subcontractAdv,
            category_employee: subcontractOther,
          };

          arrSubcontarctAll.push(contractObj);
        } else {
          var choseNameSubcontract =
            nameSubcontract.options[nameSubcontract.selectedIndex].getAttribute(
              "data-id"
            );

          if (contractChild[0].value == "adv") {
            subcontractAdv = choseNameSubcontract;
            subcontractOther = null;
          } else {
            subcontractOther = choseNameSubcontract;
            subcontractAdv = null;
          }
          let amount = contractChild[3].value
            .replace(/[^+\d]/g, "")
            .replace(/(\d)\++/g, "$1");

          const contractObj = {
            id: "",
            month_bill: idBill,
            amount: amount,
            platform: subcontractAdv,
            category_employee: subcontractOther,
          };

          arrSubcontarctAll.push(contractObj);
        }
      }
    });

    const endpoint = "/api/v1/subcontract/upd_subs/";
    let csrfToken = getCookie("csrftoken");
    let data = JSON.stringify(arrSubcontarctAll);
    console.log();

    fetch(endpoint, {
      method: "POST",
      body: data,
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
        }, 200);
      } else {
        const windowContent = document.getElementById(elem);

        alertError(windowContent);
        const timerId = setTimeout(() => {
          location.reload();
        }, 200);
      }
    });
      // .then((response) => response.json())
      // .then((data) => {
      //   const updBill = {
      //     id: idBill,
      //     chekin_add_subcontr: true,
      //   };
      //   // чекин о заполнении субкотрактов
      //   const endpoint = "/service/api/month_bill/" + idBill + "/";
      //   let csrfToken = getCookie("csrftoken");
      //   let data2 = JSON.stringify(updBill);
      //   fetch(endpoint, {
      //     method: "PUT",
      //     body: data2,
      //     headers: {
      //       "Content-Type": "application/json",
      //       "X-CSRFToken": csrfToken,
      //     },
      //   }).then((response) => {
      //     if (response.ok === true) {
      //       const windowContent = document.getElementById(elem);
      //       alertSuccess(windowContent);
      //       const timerId = setTimeout(() => {
      //         location.reload();
      //       }, 200);
      //     } else {
      //       const windowContent = document.getElementById(elem);

      //       alertError(windowContent);
      //       const timerId = setTimeout(() => {
      //         location.reload();
      //       }, 200);
      //     }
      //   });
      // });
  });
}
// проверка получение страых субконтрактов- если нет обычное окно  отрисовка на фронте
function getOldSumcintract(idBill, element, elem) {
  preloaderModal((isLoading = true), (isLoaded = false));

  const endpoint = "/api/v1/subcontract/" + idBill + "/subcontract_li/";
  console.log(endpoint)
  let csrfToken = getCookie("csrftoken");
  fetch(endpoint, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken,
    },
  })
    .then((response) => response.json(
      console.log(response)
    ))
    .then((data) => {
      if (data.length == 0) {
        preloaderModal((isLoading = false), (isLoaded = true));
        console.log("data",data)
        //  observerChangeCreateInput(element);
        return;
      } else {
        console.log("else")
        let endpoint = "/api/v1/adv-platform/adv/";
        fetch(endpoint, {
          method: "get",
        })
          .then((response) => response.json())
          .then((dataCategoryAdv) => {
            console.log("dataCategoryAdv", dataCategoryAdv)
            const c = document.querySelector(".modal_add_subcontract_wrapper");
            c.innerHTML = "";
            console.log("data", data)
            data.forEach(function (value, key) {
              
              let modal_add_subcontract = document.createElement("div");
              modal_add_subcontract.className =
                "modal_add_contract modal_add-subcontract";
              c.append(modal_add_subcontract);

              preloaderModal((isLoading = false), (isLoaded = true));

              if (value.platform != null) {
                modal_add_subcontract.innerHTML =
                  '<input type="text" readonly class="modal-subcontracts input-130" placeholder="adv" value="площадка" data-adv="adv">';
                dataCategoryAdv.forEach((item) => {
                  if (item.id == value.platform) {
                    console.log(item.id, value.platform)
                    new Input(
                      "text",
                      "modal-subcontracts   input-130 subs-old ",
                      item.name,
                      "сумма",
                      true,
                      item.id
                    ).appendTo(modal_add_subcontract);

                    new Input(
                      "text",
                      "modal-subcontracs modal-subcontract-input_sum input-200 num_budet pyb",
                      value.amount,
                      "сумма"
                    ).appendTo(modal_add_subcontract);

                    new Input("hidden", "subcontract_id", value.id).appendTo(
                      modal_add_subcontract
                    );
                    let prevOperationDel = document.createElement("div");
                    prevOperationDel.className = "subcontract_del";

                    modal_add_subcontract.append(prevOperationDel);
                    prevOperationDel.setAttribute("data-id-peration", value.id);
                    prevOperationDel.innerHTML = "+";
                    console.log("modal_add_subcontract", modal_add_subcontract)
                  }
                });
                // observerChangeCreateInput(element);
                replaceNam();
              } else {
                // старые субконтракты для категории другое
                let endpoint = "/api/v1/adv-platform/other/";
                fetch(endpoint, {
                  method: "get",
                })
                  .then((response) => response.json())
                  .then((dataCategoryOther) => {
                    dataCategoryOther.forEach((item) => {
                      if (item.id == value.category_employee) {
                        modal_add_subcontract.innerHTML =
                          '<input type="text" readonly class="modal-subcontracts input-130" placeholder="other" value="премия" data-adv="other">';
                        new Input(
                          "text",
                          "modal-subcontracts   input-130 subs-old",
                          item.name,
                          "сумма",
                          true,
                          item.id
                        ).appendTo(modal_add_subcontract);
                        new Input(
                          "text",
                          "modal-subcontracs input-200 pyb",
                          value.amount,
                          "сумма"
                        ).appendTo(modal_add_subcontract);

                        new Input(
                          "hidden",
                          "subcontract_id",
                          value.id
                        ).appendTo(modal_add_subcontract);

                        let prevOperationDel = document.createElement("div");
                        prevOperationDel.className = "subcontract_del";

                        modal_add_subcontract.append(prevOperationDel);
                        prevOperationDel.setAttribute(
                          "data-id-peration",
                          value.id
                        );
                        prevOperationDel.innerHTML = "+";
                      }
                    });
                    replaceNam();
                    DelSubcontr(element, elem);
                    // observerChangeCreateInput(element);
                  });

                preloaderModal((isLoading = false), (isLoaded = true));
              }
            });

            DelSubcontr(element, elem);

            const title = document.querySelector("#page_name").value;
            if (title == "1") {
              // установка бюджета без запланироывнныфх трат
              let sumAdv = element.getAttribute("data-bill-month-adv");
              let sumAdvReplace = sumAdv.replace(/\s+/g, "");
              sumOld = +sumAdvReplace;
              const numBudetAll = document.querySelectorAll(".num_budet");

              if (numBudetAll) {
                numBudetAll.forEach((el) => {
                  sumOld -= +el.value
                    .replace(/[^+\d]/g, "")
                    .replace(/(\d)\++/g, "$1");
                });
              }
              let useBudget = document.querySelector(
                ".modal_adv_budget_not_use"
              );
              let useBudgetAfterUse =
                document.getElementById("sum_adv_after_use");
              useBudgetAfterUse.value = sumOld;
              var result = sumOld.toLocaleString();
              useBudget.innerHTML = result + " ₽";
              // useBudget.innerHTML = sumOld;
              const slash = document.querySelector(
                ".modal_adv_budget_not_use_slash"
              );
              slash.style.display = "block";
              // observerChangeCreateInput(element);
            }

            let modal_add_subcontract = document.createElement("div");
            modal_add_subcontract.className =
              "modal_add_contract modal_add-subcontract";
            c.append(modal_add_subcontract);

            let modal_add_subcontract_select = document.createElement("select");
            modal_add_subcontract_select.className =
              "modal-subcontract-type choice";
            modal_add_subcontract.append(modal_add_subcontract_select);

            new selectOption(
              "modal-select empty",
              0,
              "",
              "Тип",
              0,
              false
            ).appendTo(modal_add_subcontract_select);
            new selectOption(
              "modal-select",
              "adv",
              "",
              "площадка",
              "selected",
              false
            ).appendTo(modal_add_subcontract_select);

            new selectOption(
              "modal-select ",
              "other",
              "",
              "премия",
              "selected",
              false
            ).appendTo(modal_add_subcontract_select);

            createInputSubcontract();
          });
      }
    });
}

// категории субконтрактов если есть заполненные
function FetchCatSubsOther() {
  let endpoint = "/api/v1/adv-platform/other/";
  fetch(endpoint, {
    method: "get",
  })
    .then((response) => response.json())
    .then((dataCategoryOther) => {
      return dataCategoryOther;
    });
}
// удаление субкотнрактов
function DelSubcontr(element, elem) {
  const delButton = document.querySelectorAll(".subcontract_del");
  delButton.forEach((item) => {
    item.addEventListener("click", () => {
      idOperation = item.getAttribute("data-id-peration");

      endpoint = "/api/v1/subcontract/" + idOperation + "/";

      let csrfToken = getCookie("csrftoken");

      fetch(endpoint, {
        method: "DELETE",

        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
      }).then((response) => {
        if (response.ok === true) {
          item.parentElement.remove();
          const add_operation = document.querySelector(".subcontarct_add");
          add_operation.replaceWith(add_operation.cloneNode(true));
          // имитация клика по первичной графе запуск функции заново
          // запись в локал тригера для перезагрузки после закрытия. имитация повторного клика для обновления модалки
          localStorage.setItem("changeInfo", true);
          element.click();

          return;
        } else {
          const windowContent = document.getElementById(elem);
          DontDelite(windowContent);
        }
      });
    });
  });
}
