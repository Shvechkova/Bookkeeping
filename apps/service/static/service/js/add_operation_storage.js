const addOperationStorage = document.querySelectorAll(".add-operation-storage");

if (addOperationStorage) {
    addOperationStorage.forEach((element) => {
    element.addEventListener("click", () => {
      console.log(element)
    
      // заполнение тайтла инфой

      getBillInfoOutOperStorage(element);
      document.getElementById("date-operation_out_storage").valueAsDate = new Date();
      // очистка старых операций
      const lastOperationWrap = document.querySelector(
        ".previous_operation_out_storage"
      );
      lastOperationWrap.innerHTML = "";

      let elem = element.getAttribute("data-name");
      // let operationIdvalue = element.getAttribute(
      //   "data-bill-month-operation-entry"
      // );

      // открытие модалки
      const add_operation = document.querySelector(".add-operation-storage_out");
      add_operation.disabled = true
      modal(elem, add_operation);

      // выбор радио кнопки если вводить другое значение
      const nameElemOtherSumst = "other_sum_namber_out_storage";
      const nameRadioOtherSumst = "other_sum_out_storage";
      ChekinOtherSum(nameElemOtherSumst, nameRadioOtherSumst);
      const chekinOtherSum = document.getElementById("other_sum_out_storage");
      chekinOtherSum.addEventListener("input", () => {
        const chekinOtherSum = document.getElementById("other_sum");

        chekinOtherSum.checked = true;
      });
      // добавление операции
      console.log("добавление операции")
      newOperationOutStorage(element, elem);
      // получение старых операций

      const endpointOperation = "/api-bookkeeping/v1/operation/operation_save/";
      addFetchOperationOutStorage(element, endpointOperation, elem);

      // валидация радиокнопок
      const modalWindows = document.getElementById(elem);
      modalWindows.addEventListener("input", () => {
        validateRadio(
          elem,
          ".add-operation-storage_out",
          ".input_bank_wrap_one_storage",
          ".input_bank_wrap_storage"
        );
      });
    });
  });
}
// заполнение инфой тайтла
function getBillInfoOutOperStorage(element) {
  const clientName = element.getAttribute("data-bill-month-client-name");
  const contractName = element.getAttribute("data-bill-month-name");
  const contractData = element.getAttribute("data-bill-month-data");
  const allMonthSum = element.getAttribute("data-bill-month-diff-sum");
  const nameSumorder = element.getAttribute("data-name-sub");
  console.log(clientName)
  const modalClient = document.querySelector(
    ".operation_entry_client-name_out_storage"
  );
  const modalContract = document.querySelector(
    ".operation_entry_contract-name_out_storage"
  );
  const modalData = document.querySelector(".operation_entry_data_out_storage");

  const modalNameSuborder = document.querySelector(".name_suborder_modal_out_storage");
  const modalSumCtr = document.querySelector(".sum_operation_suborders_outs_storage");
  const modalsunordrt_operation_all = document.querySelector(
    ".sum_operation_suborders_all_storage"
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


// добавление операции
function addFetchOperationOutStorage(element, endpoint, elem) {
  let idSuborder = element.getAttribute("data-idsuborder-sub");
  const btnAddOperationEntry = document.querySelector(".add-operation-storage_out");
  // const allMonthSum = element.getAttribute(
  //   "name_suborder_modal"
  // );
  const billId = element.getAttribute("data-bill-month-id");
  const billMonthId = element.getAttribute("data-bill-month-id");

  btnAddOperationEntry.addEventListener("click", () => {
    const allMonthSum = element.getAttribute("data-bill-month-diff-sum");
    let bankChecked;
    const bankElement = document.querySelectorAll(
      '#bank_cheked_out_storage input[name="bank"]'
    );
    bankElement.forEach((el) => {
      if (el.checked) {
        bankChecked = el.value;
      }
    });
    let sumChecked;
    const sumChekedInp = document.getElementById("sum_cheked_out_storage");
    const stepCheked = sumChekedInp.getAttribute("data-step");

    const sumElement = document.querySelectorAll(
      '#sum_cheked_out_storage input[name="sum"]'
    );

    // let intMonthSum = allMonthSum.replace(/[^0-9]/g, "");
    let intMonthSum = getCurrentPrice(allMonthSum)
    // если первое добавление операции
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
              "#other_sum_namber_out_storage"
            );
            sumChecked = +otherSumCheck.value;

            return;
          }
        }
      });
      // если уже есть операции
    } else if (stepCheked == "2") {
      sumElement.forEach((el) => {
        if (el.checked) {
          if (el.value > "1") {
            sumChecked = +el.value;

            return;
          } else {
            const otherSumCheck = document.querySelector(
              "#other_sum_namber_out_storage"
            );
            sumChecked = +otherSumCheck.value;
            return;
          }
        }
      });
    }

    const commentOperation = document.getElementById(
      "operation_comment_out_storage"
    ).value;
    
    const data_select = document.getElementById("date-operation_out_storage").value;
    const form = new FormData();
    // form.append("amount", sumChecked);
    // form.append("comment", commentOperation);
    // form.append("bank", bankChecked);
    // form.append("suborder", billId);
    // form.append("monthly_bill", billMonthId);
    // form.append("type_operation", "out");
    // form.append("data", data_select);
    // form.append("meta_categ", "oper_account");
    // form.append("suborder", +idSuborder);
    form.append("data", data_select);
    form.append("bank_in", bankChecked);
    form.append("bank_to", 4);
    form.append("amount", sumChecked);
    form.append("comment", commentOperation);
    form.append("monthly_bill", +billId);
    // form.append("storage", true);


    let object = {};
    form.forEach((value, key) => (object[key] = value));
    const dataJson = JSON.stringify(object);
    console.log(dataJson);
    let csrfToken = getCookie("csrftoken");
console.log(commentOperation);
    fetch(endpoint, {
      method: "POST",
      body: dataJson,
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
    })
      // .then((response) => response.json())
      // .then((data) => {
      //   console.log(data);
      // });
      .then((response) => {
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

function newOperationOutStorage(element, elem) {
  console.log(999999)
  let billId = element.getAttribute("data-bill-month-id"); 
  let operationIdvalue = element.getAttribute("data-id-sub");
  let operationAllSum = element.getAttribute("data-id-sub-amount");
  const idOperationrepl = operationIdvalue.replace(
    /^\D+|[^\d-]+|-(?=\D+)|\D+$/gim,
    ""
  );
  let st = getCurrentPrice(operationAllSum);
  let sum_all = getCurrentPrice(operationAllSum);
  console.log("operationAllSum",operationAllSum)
  console.log("sum_all,sum_all",sum_all)
  if (billId !== "") {
    let data = new FormData();
    let object = {
      monthly_bill: billId,
      storage: true,
    };

    const dataJson = JSON.stringify(object);
    preloaderModal(isLoading = true, isLoaded = false)
    let csrfToken = getCookie("csrftoken");
    fetch("/api-bookkeeping/v1/operation/operation_out_filter/", {
      method: "POST",
      body: dataJson,
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
    })
      .then((response) => response.json())
      .then((data) => {
        console.log(2222222222222222222222222)
        console.log(data);
        if (data.length > 0) {
          preloaderModal(isLoading = false, isLoaded = true)
          const lastOperationWrap = document.querySelector(
            ".previous_operation_out_storage"
          );
          lastOperationWrap.innerHTML = "";
          console.log(data)
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
              operationAllSum +
              " ₽";

            let comment = item.comment;

            let prevOperationComm = document.createElement("div");
            prevOperationComm.className = "previous_operation_comment";
            prevOperationiNoComm.append(prevOperationComm);
            if (comment != null & comment != "") {
              prevOperationComm.innerHTML = "Комментарий: " + comment;
            }
            st -= +sumoperation;
          });
          preloaderModal(isLoading = false, isLoaded = true)

          DelOperationOutStorage(element);
          sumOperationEnded = st;

          const sumExpected = document.querySelector(
            ".sum_operation_suborders_all_storage"
          );
          console.log("sum_all",sum_all)
          console.log("sumOperationEnded",sumOperationEnded)
          var t = sum_all - sumOperationEnded;
          console.log("t",t)

          if (sumOperationEnded == 0) {
            const sumallred = document.querySelector(
              ".sum_operation_suborders_outs_storage"
            );
            sumallred.style.color = "black";
          }
          var num = +t;
          console.log("num",num)
          var result = num.toLocaleString();
          console.log("result",result)
          sumExpected.innerHTML = result + " ₽";

          const sumChekedWrap = document.getElementById("sum_cheked_out_storage");
          sumChekedWrap.setAttribute("data-step", "2");
          sumChekedWrap.innerHTML =
            '<h3>Сколько перевели?</h3><div class="input_bank_wrap_storage"><input checked type="radio" id="100_out_storage" name="sum" value="' +
            sumOperationEnded +
            '" /><label for="100_out_storage">Остаток</label><input type="radio" id="other_sum_out_storage" name="sum" value="1" /><input placeholder="Другая сумма" data-validate="0" type="number" id="other_sum_out_storage" name="" value="" /> </div>';

          const nameElemOtherSum = "other_sum_namber_out_storage";
          const nameRadioOtherSum = "other_sum_out_storage";
          ChekinOtherSum(nameElemOtherSum, nameRadioOtherSum);
        } else {
          const lastOperationWrap = document.querySelector(
            ".previous_operation_out_storage"
          );
          lastOperationWrap.innerHTML = "";
          console.log("9999999999999999999999999999999")
          preloaderModal(isLoading = false, isLoaded = true)
          const sumChekedWrap = document.getElementById("sum_cheked_out_storage");
          sumChekedWrap.setAttribute("data-step", "1");
          sumChekedWrap.innerHTML =
            '<h3>Сколько перевели?</h3><div class="input_bank_wrap_storage"><input type="radio" id="100_out_storage" name="sum" value="100" /><label for="100_out_storage">100%</label><input type="radio" id="50_out_storage" name="sum" value="50" /><label for="50_out_storage">50%</label><input type="radio" id="other_sum_out_storage" name="sum" value="1" /><input data-validate="0"type="number"id="other_sum_namber_out_storage"name=""value=""placeholder="Другая сумма" /></div>';

          const nameElemOtherSum = "other_sum_namber_out_storage";
          const nameRadioOtherSum = "other_sum_out_storage";
          ChekinOtherSum(nameElemOtherSum, nameRadioOtherSum);
        }

        // });
      });
  }

  return idOperationrepl;
}

function DelOperationOutStorage(element) {
  const delButton = document.querySelectorAll(".previous_operation_del");
  delButton.forEach((item) => {
    item.addEventListener("click", () => {
      idOperation = item.getAttribute("data-id-peration");
      let object = {
        "id": +idOperation,
      };
      console.log(idOperation);
      const dataJson = JSON.stringify(object);
      preloaderModal((isLoading = true), (isLoaded = false));
      endpoint = "/api-bookkeeping/v1/operation/operation_delete/";
      let csrfToken = getCookie("csrftoken");
      // endpoint = "/operations/api/operation/" + idOperation + "/";


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
          const add_operation = document.querySelector(".operation_add_out");
          add_operation.replaceWith(add_operation.cloneNode(true));
          element.click();

          return;
        }
        else {
          const windowContent = document.getElementById(elem);
          DontDelite(windowContent);
        }
      });
    });
  });
}
