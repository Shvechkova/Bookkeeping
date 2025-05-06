// субордер оплата премии для ADV
const addOperationOutPeople = document.querySelectorAll(
  ".suborder_out_operation_people"
);

if (addOperationOutPeople) {
  addOperationOutPeople.forEach((element) => {
    element.addEventListener("click", () => {
      preloaderModal((isLoading = true), (isLoaded = false));
      let elem = element.getAttribute("data-name");
      document.getElementById("date-operation_out_other").valueAsDate =
        new Date();

      const add_operation = document.querySelector(".operation_add_out_other");
      modal(elem, add_operation);

      // очистка окна от прошлых открытий
      const historySuborder = document.querySelector(".history_suborder");
      historySuborder.innerHTML = "";
      const operPrev = document.querySelector(".previous_operation_out_other");
      operPrev.innerHTML = "";
      const wrapOperOther = document.querySelector(".wrapper_oper_out_other");
      wrapOperOther.style.display = "none";

      FetchInfosubsPeople(element, elem);
      getInfoBillOperationOperOut(element);
      AddOperationOtherOut(element, elem);

      const chekinOtherSum = document.getElementById("other_sum_namber");
      chekinOtherSum.addEventListener("input", () => {
        const chekinOtherSum = document.getElementById("other_sum");

        chekinOtherSum.checked = true;
      });
      const nameElemOtherSum = "other_sum_namber_out_other";
      const nameRadioOtherSum = "other_sum_out_other";
      ChekinOtherSum(nameElemOtherSum, nameRadioOtherSum);

      // валидация радиокнопок
      const modalWindows = document.getElementById(elem);
      modalWindows.addEventListener("input", () => {
        validateRadio(
          elem,
          ".operation_add_out_other",
          ".input_bank_wrap_one_other",
          ".input_bank_wrap_other"
        );
      });
    });
  });
}
// если есть несколько сбконтрактов
function FetchInfosubsPeople(element, elem) {
  let idBill = element.getAttribute("data-bill-month-id");
  const endpoint = "/api/v1/subcontract/" + idBill + "/subcontract_li/";
  // const endpoint = "/service/api/subcontract/" + idBill + "/subcontract_li/";

  fetch(endpoint, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
      // let endpoint = "/service/api/subcontract-category-other/";
      let endpoint = "/api/v1/adv-platform/other/";
      fetch(endpoint, {
        method: "get",
      })
        .then((response) => response.json())
        .then((dataCategoryPeople) => {
          i = 0;
          data.forEach((item) => {
            if (item.category_employee != null) {
              i++;
            }
          });

          if (i > 1) {
            data.forEach((item) => {
              if (item.category_employee != null) {
                idCat = item.category_employee;
                let nameCat = "";
                dataCategoryPeople.forEach((item) => {
                  if (item.id == idCat) {
                    nameCat = item.name;
                  }
                });
                const modalSumCtr = document.querySelector(
                  ".sum_operation_suborders_outs_other"
                );

                const modalsunordrt_operation_all = document.querySelector(
                  ".sum_operation_suborders_all_other"
                );
                modalSumCtr.style.display = "none";
                modalsunordrt_operation_all.style.display = "none";
                modalsunordrt_operation_all.nextElementSibling.style.display =
                  "none";

                const historySuborderWrap =
                  document.querySelector(".history_suborder");

                let historySuborderItem = document.createElement("div");
                historySuborderItem.className = "historySuborder_item";
                historySuborderWrap.append(historySuborderItem);

                let historySuborderBtn = document.createElement("div");
                historySuborderBtn.className = "previous_operation_pay";
                historySuborderItem.append(historySuborderBtn);

                let historySuborderName = document.createElement("h3");
                historySuborderName.className = "history_suborder_name";
                historySuborderItem.append(historySuborderName);
                historySuborderName.innerHTML = nameCat;

                let historySuborderAmount = document.createElement("h3");
                historySuborderAmount.className = "history_suborder_amount";
                historySuborderItem.append(historySuborderAmount);

                var num = +item.amount;
                var result = num.toLocaleString();

                historySuborderAmount.innerHTML = result + " ₽";

                historySuborderBtn.setAttribute("data-id-cat", item.other);
                historySuborderBtn.setAttribute("data-id-subcontr", item.id);
                historySuborderBtn.setAttribute("data-id-amount", item.amount);
                historySuborderBtn.setAttribute(
                  "data-id-month-bill",
                  item.month_bill
                );
                historySuborderBtn.setAttribute("data-name-cat", nameCat);
                historySuborderBtn.innerHTML = "оплатить";
              }
            });
            const btnPaySubs = document.querySelectorAll(
              ".previous_operation_pay"
            );

            btnPaySubs.forEach((item) => {
              item.addEventListener("click", () => {
                preloaderModal((isLoading = true), (isLoaded = false));
                dataEmpty = [];
                CreateSubcontractOtherOne(
                  dataEmpty,
                  dataCategoryPeople,
                  element,
                  item
                );
              });
            });
            preloaderModal((isLoading = false), (isLoaded = true));
          } else {
            console.log(888888888888888)
            CreateSubcontractOtherOne(data, dataCategoryPeople, element);
          }
        });
    });
}
// заполнение тайтла инфой
function getInfoBillOperationOperOut(element) {
  const clientName = element.getAttribute("data-bill-month-client-name");
  const contractName = element.getAttribute("data-bill-month-name");
  const contractData = element.getAttribute("data-bill-month-data");
  const allMonthSum = element.getAttribute("data-id-sub-amount");
  const nameSumorder = element.getAttribute("data-name-sub");

  const modalClient = document.querySelector(
    ".operation_entry_client-name_out_other"
  );
  const modalContract = document.querySelector(
    ".operation_entry_contract-name_out_other"
  );
  const modalData = document.querySelector(".operation_entry_data_out_other");

  const modalNameSuborder = document.querySelector(
    ".name_suborder_modal_out_other"
  );
  const modalSumCtr = document.querySelector(
    ".sum_operation_suborders_outs_other"
  );
  const modalsunordrt_operation_all = document.querySelector(
    ".sum_operation_suborders_all_other"
  );

  modalClient.innerHTML = clientName;
  modalContract.innerHTML = contractName;
  modalData.innerHTML = contractData;

  modalNameSuborder.innerHTML = nameSumorder;
  modalSumCtr.innerHTML = allMonthSum + " ₽";
  modalsunordrt_operation_all.innerHTML = 0 + " ₽";
  if (allMonthSum != modalsunordrt_operation_all) {
    modalSumCtr.style.color = "red";
  }
}
// если один субконтракт
function CreateSubcontractOtherOne(data, dataCategoryPeople, element, item) {
  console.log(data)
  const historySuborderWrap = document.querySelector(".history_suborder");
  historySuborderWrap.innerHTML = "";
  let idCat;
  let idSubcontr;
  let otherAmount;
  let monthBill;
  let nameCat = "";
  console.log("item",item);
  if (data.length == 0) {
    idCat = item.getAttribute("data-id-cat");
    idSubcontr = item.getAttribute("data-id-subcontr");
    otherAmount = item.getAttribute("data-id-amount");
    monthBill = item.getAttribute("data-id-month-bill");
    nameCat = item.getAttribute("data-name-cat");
    console.log(nameCat);
  } else {
    data.forEach((item) => {
      if (item.category_employee != null) {
        idCat = item.category_employee;
        idSubcontr = item.id;
        otherAmount = item.amount;
        monthBill = item.month_bill;
      }
    });

    dataCategoryPeople.forEach((item) => {
      if (item.id == idCat) {
        nameCat = item.name;
      }
    });
  }

  const wrapOperOther = document.querySelector(".wrapper_oper_out_other");

  wrapOperOther.style.display = "block";
  const modalNameSuborder = document.querySelector(
    ".name_suborder_modal_out_other"
  );
  modalNameSuborder.innerHTML = "Премия " + nameCat;
  wrapOperOther.setAttribute("data-id-sub-other", idSubcontr);
  wrapOperOther.setAttribute("data-id-sub-amount-id", otherAmount);
  wrapOperOther.setAttribute("data-bill-month-id", monthBill);

  if (data.length == 0) {
    const modalSumCtr = document.querySelector(
      ".sum_operation_suborders_outs_other"
    );
    const modalsunordrt_operation_all = document.querySelector(
      ".sum_operation_suborders_all_other"
    );

    modalSumCtr.innerHTML = otherAmount + " ₽";
    modalsunordrt_operation_all.innerHTML = 0 + " ₽";
    if (otherAmount != modalsunordrt_operation_all) {
      modalSumCtr.style.color = "red";
    }
  }

  NewOperationOutOther(element);
}
// отправка добавление операций
function AddOperationOtherOut(element, elem) {
  const btnAddOperationOut = document.querySelector(".operation_add_out_other");
  const wrapOperOther = document.querySelector(".wrapper_oper_out_other");

  btnAddOperationOut.addEventListener("click", () => {
    const allMonthSum = wrapOperOther.getAttribute("data-id-sub-amount-id");
    const billId = wrapOperOther.getAttribute("data-id-sub-other");
    const billMonthId = wrapOperOther.getAttribute("data-bill-month-id");
    let bankChecked;
    const bankElement = document.querySelectorAll(
      '#bank_cheked_out_other input[name="bank"]'
    );
    bankElement.forEach((el) => {
      if (el.checked) {
        bankChecked = el.value;
      }
    });
    let sumChecked;
    const sumChekedInp = document.getElementById("sum_cheked_out_other");
    const stepCheked = sumChekedInp.getAttribute("data-step");

    const sumElement = document.querySelectorAll(
      '#sum_cheked_out_other input[name="sum"]'
    );

    let intMonthSum = parseInt(allMonthSum);

    if (stepCheked == "1") {
      sumElement.forEach((el) => {
        if (el.checked) {
          if (el.value == "100") {
            sumChecked = +intMonthSum;

            return;
          } else if (el.value == "50") {
            sumChecked = +intMonthSum / 2;
            return;
          } else {
            const otherSumCheck = document.querySelector(
              "#other_sum_namber_out_other"
            );
            sumChecked = +otherSumCheck.value;

            return;
          }
        }
      });
    } else if (stepCheked == "2") {
      sumElement.forEach((el) => {
        if (el.checked) {
          if (el.value > "1") {
            sumChecked = +el.value;

            return;
          } else {
            const otherSumCheck = document.querySelector(
              "#other_sum_namber_out"
            );
            sumChecked = +otherSumCheck.value;
            return;
          }
        }
      });
    }

    const commentOperations = document.getElementById(
      "operation_comment_out_other"
    ).value;
    let commentOperation = "";
    if (commentOperations != "") {
      const nameSubs = document.querySelector(
        ".name_suborder_modal_out"
      ).textContent;
      commentOperation = nameSubs + " - " + commentOperations;
    } else {
      commentOperation = commentOperations;
    }

    const data_select = document.getElementById(
      "date-operation_out_other"
    ).value;
    console.log(999999888888)
    console.log("commentOperation",commentOperation)
    const form = new FormData();
    // form.append("amount", sumChecked);
    // form.append("comment", commentOperation);
    // form.append("bank", bankChecked);
    // form.append("suborder", billId);
    // form.append("monthly_bill", billMonthId);
    // form.append("type_operation", "out");
    // form.append("data", data_select);
 
    form.append("suborder", +billId);
    form.append("data", data_select);
    form.append("bank_in", bankChecked);
    form.append("bank_to", 5);
    form.append("amount", sumChecked);
    form.append("comment", commentOperation);
    form.append("monthly_bill", +billMonthId);

    let object = {};
    form.forEach((value, key) => (object[key] = value));
    const dataJson = JSON.stringify(object);

    let csrfToken = getCookie("csrftoken");
    // const endpoint = "/operations/api/operation/";
    const endpoint= "/api/v1/operation/operation_save/";
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
        }, 200);
      } else {
        const windowContent = document.getElementById(elem);

        alertError(windowContent);
        const timerId = setTimeout(() => {
          location.reload();
        }, 200);
      }
    });
  });
}
// получение старых операций
function NewOperationOutOther(element) {
  const wrapOperOther = document.querySelector(".wrapper_oper_out_other");
  let operationAllSum = wrapOperOther.getAttribute("data-id-sub-amount-id");
  const modalSumCtr = document.querySelector(
    ".sum_operation_suborders_outs_other"
  );

  const modalsunordrt_operation_all = document.querySelector(
    ".sum_operation_suborders_all_other"
  );
  modalSumCtr.style.display = "block";
  modalsunordrt_operation_all.style.display = "block";
  modalsunordrt_operation_all.nextElementSibling.style.display = "block";
  let idSuborder = element.getAttribute("data-idsuborder-sub");
  let operationIdvalue = wrapOperOther.getAttribute("data-id-sub-other");
  let st = parseInt(operationAllSum);
  let sum_all = parseInt(operationAllSum);
  const billId = element.getAttribute("data-bill-month-id");
  if (operationIdvalue !== "") {
    let data = new FormData();
    let object = {
      id: operationIdvalue,
    };
    let object2 = {
      "monthly_bill": +billId,
      // "platform": +operationNameCAt,
      "id": + idSuborder,
      "category_employee": true,

    };

    const dataJson = JSON.stringify(object2);

    let csrfToken = getCookie("csrftoken");
    fetch("/api/v1/operation/operation_out_filter/", {
      method: "POST",
      body: dataJson,
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
    })
      .then((response) => response.json())
      .then((data) => {
        // заполнение полученными старыми операциями
        if (data.length > 0) {
          const lastOperationWrap = document.querySelector(
            ".previous_operation_out_other"
          );
          lastOperationWrap.innerHTML = "";

          data.forEach((item) => {
            var options = {
              day: "numeric",
              month: "long",
              year: "numeric",
            };
            var d = new Date(item.created_timestamp);
            const sumoperation = item.amount;
            var num = +sumoperation;
            var result = num.toLocaleString();
            var numAll = +operationAllSum;
            var numAllsum = numAll.toLocaleString();
            // враппер для коментария
            let dataOperation = d.toLocaleString("ru", options);
            let prevOperationItem = document.createElement("div");
            prevOperationItem.className = "previous_operation_item";
            lastOperationWrap.append(prevOperationItem);
            // кнопка удалить
            let prevOperationDel = document.createElement("div");
            prevOperationDel.className = "previous_operation_del";
            prevOperationItem.append(prevOperationDel);
            prevOperationDel.setAttribute("data-id-peration", item.id);
            prevOperationDel.innerHTML = "+";

            let prevOperationiNoComm = document.createElement("div");
            prevOperationiNoComm.className = "previous_operation_wrap";
            prevOperationItem.append(prevOperationiNoComm);

            let prevOperationTitle = document.createElement("div");
            prevOperationTitle.className = "previous_operation_title";
            prevOperationiNoComm.append(prevOperationTitle);
            prevOperationTitle.innerHTML =
              dataOperation +
              " - оплата " +
              result +
              " ₽ из " +
              numAllsum +
              " ₽";

            let comment = item.comment;

            let prevOperationComm = document.createElement("div");
            prevOperationComm.className = "previous_operation_comment";
            prevOperationiNoComm.append(prevOperationComm);
            if (comment != null & comment != "") {
              prevOperationComm.innerHTML = "Комментарий: " + comment;
              // const commentSplit = comment.split("-");
              // console.log(commentSplit.length);
              // if (commentSplit.length > 1) {
              //   commentSplit.shift();
              //   prevOperationComm.innerHTML = "Комментарий: " + commentSplit;
              // } else {
              //   prevOperationComm.innerHTML = "Комментарий: " + comment;
              // }
            }
            st -= +sumoperation;
          });

          DelOperationOutOther(element);
          sumOperationEnded = st;

          const sumExpected = document.querySelector(
            ".sum_operation_suborders_all_other"
          );

          var t = operationAllSum - sumOperationEnded;
          console.log(9999,operationAllSum,sumOperationEnded)
          const sumallred = document.querySelector(
            ".sum_operation_suborders_outs_other"
          );
          if (sumOperationEnded == 0) {
            sumallred.style.color = "black";
          }
          var num = +t;
          var result = num.toLocaleString();

          sumExpected.innerHTML = result + " ₽";
          var num = +operationAllSum;
          var result = num.toLocaleString();

          sumallred.innerHTML = result + " ₽";

          const sumChekedWrap = document.getElementById("sum_cheked_out_other");
          sumChekedWrap.setAttribute("data-step", "2");
          sumChekedWrap.innerHTML =
            '<h3>Сколько оплатили?</h3><div class="input_bank_wrap_other"><input checked type="radio" id="100_out_other" name="sum" value="' +
            sumOperationEnded +
            '" /><label for="100_out_other">Остаток</label><input type="radio" id="other_sum_out_other" name="sum" value="1" /><input data-validate="0" type="number" id="other_sum_namber_out_other" name="" value="" placeholder="Другая сумма"  /></div>';

          const nameElemOtherSum = "other_sum_namber_out_other";
          const nameRadioOtherSum = "other_sum_out_other";
          ChekinOtherSum(nameElemOtherSum, nameRadioOtherSum);
          preloaderModal((isLoading = false), (isLoaded = true));
        } else {
          // отрисовка модалки если нет старых операций
          const lastOperationWrap = document.querySelector(
            ".previous_operation_out_other"
          );
          lastOperationWrap.innerHTML = "";
          const sumChekedWrap = document.getElementById("sum_cheked_out_other");
          sumChekedWrap.setAttribute("data-step", "1");
          sumChekedWrap.innerHTML =
            '<h3>Сколько оплатили?</h3> <div class="input_bank_wrap_other"><input  type="radio" id="100_out_other" name="sum" value="100" /><label for="100_out_other">100%</label><input type="radio" id="50_out_other" name="sum" value="50" /><label for="50_out_other">50%</label><input type="radio" id="other_sum_out_other" name="sum" value="1" /><input data-validate="0"  type="number" id="other_sum_namber_out_other" name="" value="" placeholder="Другая сумма" /></div>';

          const nameElemOtherSum = "other_sum_namber_out_other";
          const nameRadioOtherSum = "other_sum_out_other";
          ChekinOtherSum(nameElemOtherSum, nameRadioOtherSum);
          preloaderModal((isLoading = false), (isLoaded = true));
        }

        // });
      });
  }
}
// удаление операций
function DelOperationOutOther(element) {
  const delButton = document.querySelectorAll(".previous_operation_del");
  delButton.forEach((item) => {
    item.addEventListener("click", () => {
      idOperation = item.getAttribute("data-id-peration");
      let object = {
        "id": +idOperation,
      };
      // endpoint = "/operations/api/operation/" + idOperation + "/";
      endpoint = "/api/v1/operation/operation_delete/";
      let csrfToken = getCookie("csrftoken");
      const dataJson = JSON.stringify(object);
      fetch(endpoint, {
        method: "POST",
        body: dataJson,

        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
      }).then((response) => {
        if (response.ok === true) {
          item.parentElement.remove();
          const add_operation = document.querySelector(
            ".operation_add_out_other "
          );
          add_operation.replaceWith(add_operation.cloneNode(true));

           // запись в локал тригера для перезагрузки после закрытия. имитация повторного клика для обновления модалки
           localStorage.setItem("changeInfo", true);
          element.click();
          return;
        }else {
          const windowContent = document.getElementById(elem);
          DontDelite(windowContent);
        }
      });
    });
  });
}
