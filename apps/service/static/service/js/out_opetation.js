const addOperationOut = document.querySelectorAll(".suborder_out_operation");

if (addOperationOut) {
  addOperationOut.forEach((element) => {
    element.addEventListener("click", () => {
      console.log(2434441);
      preloaderModal((isLoading = true), (isLoaded = false));
      // заполнение тайтла инфой
      // getInfoBillOperationOperOut(element);
      getBillInfoOutOper(element);
      document.getElementById("date-operation_out").valueAsDate = new Date();
      // очистка старых операций
      const lastOperationWrap = document.querySelector(
        ".previous_operation_out"
      );
      lastOperationWrap.innerHTML = "";

      let elem = element.getAttribute("data-name");
      // let operationIdvalue = element.getAttribute(
      //   "data-bill-month-operation-entry"
      // );

      // открытие модалки
      const add_operation = document.querySelector(".operation_add_out");
      add_operation.disabled = true;
      modal(elem, add_operation);

      // выбор радио кнопки если вводить другое значение
      const nameElemOtherSum = "other_sum_namber_out";
      const nameRadioOtherSum = "other_sum_out";
      ChekinOtherSum(nameElemOtherSum, nameRadioOtherSum);
      const chekinOtherSum = document.getElementById("other_sum_namber");
      chekinOtherSum.addEventListener("input", () => {
        const chekinOtherSum = document.getElementById("other_sum");

        chekinOtherSum.checked = true;
      });
      // добавление операции
      console.log("newOperationOut")
      newOperationOutStorage(element, elem);
      // получение старых операций

      const endpointOperation = "/operations/api/operation/operation_out/";
      addFetchOperationOut(element, endpointOperation, elem);

      // валидация радиокнопок
      const modalWindows = document.getElementById(elem);
      modalWindows.addEventListener("input", () => {
        validateRadio(
          elem,
          ".operation_add_out",
          ".input_bank_wrap_one",
          ".input_bank_wrap"
        );
      });
    });
  });
}
// заполнение инфой тайтла
function getBillInfoOutOper(element) {
  const clientName = element.getAttribute("data-bill-month-client-name");
  const contractName = element.getAttribute("data-bill-month-name");
  const contractData = element.getAttribute("data-bill-month-data");
  const allMonthSum = element.getAttribute("data-id-sub-amount");
  const nameSumorder = element.getAttribute("data-name-sub");

  const modalClient = document.querySelector(
    ".operation_entry_client-name_out"
  );
  const modalContract = document.querySelector(
    ".operation_entry_contract-name_out"
  );
  const modalData = document.querySelector(".operation_entry_data_out");

  const modalNameSuborder = document.querySelector(".name_suborder_modal_out");
  const modalSumCtr = document.querySelector(".sum_operation_suborders_outs");
  const modalsunordrt_operation_all = document.querySelector(
    ".sum_operation_suborders_all"
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
function addFetchOperationOut(element, endpoint, elem) {
  const btnAddOperationEntry = document.querySelector(".operation_add_out");
  // const allMonthSum = element.getAttribute(
  //   "name_suborder_modal"
  // );
  const billId = element.getAttribute("data-id-sub");
  const billMonthId = element.getAttribute("data-bill-month-id");

  btnAddOperationEntry.addEventListener("click", () => {
    const allMonthSum = element.getAttribute("data-id-sub-amount");
    let bankChecked;
    const bankElement = document.querySelectorAll(
      '#bank_cheked_out input[name="bank"]'
    );
    bankElement.forEach((el) => {
      if (el.checked) {
        bankChecked = el.value;
      }
    });
    let sumChecked;
    const sumChekedInp = document.getElementById("sum_cheked_out");
    const stepCheked = sumChekedInp.getAttribute("data-step");

    const sumElement = document.querySelectorAll(
      '#sum_cheked_out input[name="sum"]'
    );

    let intMonthSum = allMonthSum.replace(/[^0-9]/g, "");
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
              "#other_sum_namber_out"
            );
            sumChecked = +otherSumCheck.value
              .replace(/[^+\d]/g, "")
              .replace(/(\d)\++/g, "$1");

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
              "#other_sum_namber_out"
            );
            sumChecked = +otherSumCheck.value
              .replace(/[^+\d]/g, "")
              .replace(/(\d)\++/g, "$1");
            return;
          }
        }
      });
    }

    const commentOperations = document.getElementById(
      "operation_comment_out"
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

    const data_select = document.getElementById("date-operation_out").value;
    const form = new FormData();
    form.append("amount", sumChecked);
    form.append("comment", commentOperation);
    form.append("bank", bankChecked);
    form.append("suborder", billId);
    form.append("monthly_bill", billMonthId);
    form.append("type_operation", "out");
    form.append("data", data_select);
    form.append("meta_categ", "suborders");

    let object = {};
    form.forEach((value, key) => (object[key] = value));
    const dataJson = JSON.stringify(object);
    console.log(dataJson);
    let csrfToken = getCookie("csrftoken");

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
  console.log(123456789)
  let operationIdvalue = element.getAttribute("data-id-sub");
  let operationAllSum = element.getAttribute("data-id-sub-amount");
  console.log("operationIdvalue",operationIdvalue)
  const idOperationrepl = operationIdvalue.replace(
    /^\D+|[^\d-]+|-(?=\D+)|\D+$/gim,
    ""
  );
  let st = parseInt(operationAllSum.replace(/\s+/g, ""), 10);
  let sum_all = parseInt(operationAllSum.replace(/\s+/g, ""), 10);
  console.log(idOperationrepl);
  if (idOperationrepl !== "") {
    let data = new FormData();
    let object = {
      id: idOperationrepl,

    };

    const dataJson = JSON.stringify(object);
    preloaderModal((isLoading = true), (isLoaded = false));
    let csrfToken = getCookie("csrftoken");
    fetch("/operations/api/operation/operation_out_filter/", {
      method: "POST",
      body: dataJson,
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
    })
      .then((response) => response.json())
      .then((data) => {
        console.log(data);
        if (data.length > 0) {
          // preloaderModal(isLoading = false, isLoaded = true)
          const lastOperationWrap = document.querySelector(
            ".previous_operation_out"
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
            if (comment != "") {
            
              const commentSplit = comment.split("-");
              console.log(commentSplit.length)
              if (commentSplit.length > 1){
                commentSplit.shift();
                prevOperationComm.innerHTML = "Комментарий: " + commentSplit;
              } else {
                prevOperationComm.innerHTML = "Комментарий: " + comment;
              }
              
              // prevOperationComm.innerHTML = "Комментарий: " + commentSplit;
            }
            st -= +sumoperation;
          });
          // preloaderModal(isLoading = false, isLoaded = true)

          DelOperationOut(element);
          sumOperationEnded = st;

          const sumExpected = document.querySelector(
            ".sum_operation_suborders_all"
          );

          var t = sum_all - sumOperationEnded;

          if (sumOperationEnded == 0) {
            const sumallred = document.querySelector(
              ".sum_operation_suborders_outs"
            );
            sumallred.style.color = "black";
          }
          var num = +t;
          var result = num.toLocaleString();
          sumExpected.innerHTML = result + " ₽";

          const sumChekedWrap = document.getElementById("sum_cheked_out");
          sumChekedWrap.setAttribute("data-step", "2");
          sumChekedWrap.innerHTML =
            '<h3>Сколько оплатили?</h3><div class="input_bank_wrap"><input checked type="radio" id="100_out" name="sum" value="' +
            sumOperationEnded +
            '" /><label for="100_out">Остаток</label><input type="radio" id="other_sum_out" name="sum" value="1" /><input placeholder="Другая сумма" data-validate="0" type="text" class ="pyb" id="other_sum_namber_out" name="" value="" /> </div>';

          const nameElemOtherSum = "other_sum_namber_out";
          const nameRadioOtherSum = "other_sum_out";
          replaceNam();
          ChekinOtherSum(nameElemOtherSum, nameRadioOtherSum);
          preloaderModal((isLoading = false), (isLoaded = true));
        } else {
          const sumChekedWrap = document.getElementById("sum_cheked_out");
          sumChekedWrap.setAttribute("data-step", "1");
          sumChekedWrap.innerHTML =
            '<h3>Сколько оплатили?</h3><div class="input_bank_wrap"><input  type="radio" id="100_out" name="sum" value="100" /><label for="100_out">100%</label><input type="radio" id="50_out" name="sum" value="50" /><label for="50_out">50%</label><input type="radio" id="other_sum_out" name="sum" value="1" /></label><input placeholder="Другая сумма" data-validate="0"  type="text" class="pyb" id="other_sum_namber_out" name="" value="" /></div>';

          const nameElemOtherSum = "other_sum_namber_out";
          const nameRadioOtherSum = "other_sum_out";
          replaceNam();
          ChekinOtherSum(nameElemOtherSum, nameRadioOtherSum);
          preloaderModal((isLoading = false), (isLoaded = true));
        }

        // });
      });
  }

  return idOperationrepl;
}

function DelOperationOut(element) {
  const delButton = document.querySelectorAll(".previous_operation_del");
  delButton.forEach((item) => {
    item.addEventListener("click", () => {
      idOperation = item.getAttribute("data-id-peration");
      console.log(idOperation);
      endpoint = "/operations/api/operation/" + idOperation + "/";

      fetch(endpoint, {
        method: "DELETE",
        // body: dataJson,
        headers: {
          "Content-Type": "application/json",
          // "X-CSRFToken": csrfToken,
        },
      }).then((response) => {
        if (response.ok === true) {
          item.parentElement.remove();
          const add_operation = document.querySelector(".operation_add_out");
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
