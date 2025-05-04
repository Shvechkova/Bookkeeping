choiceColor();

const addOperationEntry = document.querySelectorAll(".add-operation-entry");
if (addOperationEntry) {
  console.log(1111)
  addOperationEntry.forEach((element) => {
    element.addEventListener("click", () => {
      preloaderModal((isLoading = true), (isLoaded = false));
      document.getElementById("date-operation").valueAsDate = new Date();
      // очистка окна при повторном открытии
      const lastOperationWrap = document.querySelector(".previous_operation");
      lastOperationWrap.innerHTML = "";
      let elem = element.getAttribute("data-name");
      // let operationIdvalue = element.getAttribute(
      //   "data-bill-month-operation-entry"
      // );

      const add_operation = document.querySelector(".operation_add");
      add_operation.disabled = true;
      modal(elem, add_operation);

      const sumChek = document.querySelector("#sum_cheked");
      sumChek.setAttribute("data-step", "1");
      // учли уже ечть операции
      const chekinOtherSum = document.getElementById("other_sum_namber");
      chekinOtherSum.addEventListener("input", () => {
        const chekinOtherSum = document.getElementById("other_sum");

        chekinOtherSum.checked = true;
      });
      getOldOperation(element, elem);

      getInfoBillOperation(element);
      const endpointOperation = "/api/v1/operation/operation_save/";
      addFetchOperationEntry(element, endpointOperation, elem);

      // валидация радиокнопок
      const modalWindows = document.getElementById(elem);
      modalWindows.addEventListener("input", () => {
        validateRadio(
          elem,
          ".operation_add",
          ".input_bank_wrap_one_add",
          ".input_bank_wrap_add"
        );
      });
    });
  });
}

// заполнение тайтла инфой
function getInfoBillOperation(element) {
  const clientName = element.getAttribute("data-bill-month-client-name");
  const contractName = element.getAttribute("data-bill-month-name");
  const contractData = element.getAttribute("data-bill-month-data");
  const allMonthSum = element.getAttribute(
    "data-bill-month-sum-dont-operation"
  );

  const modalClient = document.querySelector(".operation_entry_client-name");
  const modalContract = document.querySelector(
    ".operation_entry_contract-name"
  );
  const modalData = document.querySelector(".operation_entry_data");
  const modalSumcontract = document.querySelector(".operation_entry_sum_all");

  modalClient.innerHTML = clientName;
  modalContract.innerHTML = contractName;
  modalData.innerHTML = contractData;
  modalSumcontract.innerHTML = allMonthSum + " ₽";
  modalSumcontract.style.color = "red";
}
// отправка операций
function addFetchOperationEntry(element, endpoint, elem) {
  const btnAddOperationEntry = document.querySelector(".operation_add");
  // const allMonthSum = element.getAttribute(
  //   "data-bill-month-sum-dont-operation"
  // );
  const billId = element.getAttribute("data-bill-month-id");

  btnAddOperationEntry.addEventListener("click", () => {
    const allMonthSum = element.getAttribute(
      "data-bill-month-sum-dont-operation"
    );
    let bankChecked;
    const bankElement = document.querySelectorAll(
      '#bank_cheked input[name="bank"]'
    );
    bankElement.forEach((el) => {
      if (el.checked) {
        bankChecked = el.value;
      }
    });
    let sumChecked;
    const sumChekedInp = document.getElementById("sum_cheked");
    const stepCheked = sum_cheked.getAttribute("data-step");

    const sumElement = document.querySelectorAll(
      '#sum_cheked input[name="sum"]'
    );

    let intMonthSum = allMonthSum.replace(/[^0-9]/g, "");
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
            const otherSumCheck = document.querySelector("#other_sum_namber");
            sumChecked = +otherSumCheck.value
              .replace(/[^+\d]/g, "")
              .replace(/(\d)\++/g, "$1");
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
            const otherSumCheck = document.querySelector("#other_sum_namber");
            sumChecked = +otherSumCheck.value
              .replace(/[^+\d]/g, "")
              .replace(/(\d)\++/g, "$1");
            return;
          }
        }
      });
    }

    const commentOperation = document.getElementById("operation_comment").value;
    const data_select = document.getElementById("date-operation").value;
    const form = new FormData();



    // 
    // form.append("type_operation", "entry");
    // form.append("meta_categ", "entrering");

    form.append("data", data_select);
    form.append("bank_in", "5");
    form.append("bank_to", bankChecked);
    form.append("amount", sumChecked);
    form.append("comment", commentOperation);
    form.append("monthly_bill", billId);



    let object = {};
    form.forEach((value, key) => (object[key] = value));
    const dataJson = JSON.stringify(object);

    let csrfToken = getCookie("csrftoken");

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
function getOldOperation(element, elem) {
  console.log(getOldOperation)
  const billId = element.getAttribute("data-bill-month-id");
  let operationIdvalue = element.getAttribute(
    "data-bill-month-operation-entry"
  );
  console.log(operationIdvalue)
  let operationAllSum = element.getAttribute(
    "data-bill-month-sum-dont-operation"
  );

  const idOperationrepl = operationIdvalue.replace(
    /^\D+|[^\d-]+|-(?=\D+)|\D+$/gim,
    ""
  );

  const idOperation = idOperationrepl.split("-");

  if (operationIdvalue !== "0") {
    let data = new FormData();
    let object = [];
    idOperation.forEach((item) => {
      const Obj = {
        id: item,
      };
      object.push(Obj);
    });

    let st = parseInt(operationAllSum.replace(/\s+/g, ""), 10);
    let sumOperationEnded = "";

    
    // const data_select = document.getElementById("date-now").value;
    const data_month = element.getAttribute("data-bill-month-date-month");
    const data_year = element.getAttribute("data-bill-month-date-year");
    let object2 = {
      "monthly_bill": +billId,
      "data_month": +data_month,
      "data_year": +data_year,
      "bank_in": 5,

    };

    const dataJson = JSON.stringify(object2);
    console.log(dataJson)
    let csrfToken = getCookie("csrftoken");
    fetch("/api/v1/operation/operation_entry_list/", {
      method: "POST",
      body: dataJson,
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
    })
      .then((response) => response.json())
      .then((data) => {
        const lastOperationWrap = document.querySelector(".previous_operation");
        lastOperationWrap.innerHTML = "";

        data.forEach((item) => {
          // полученые старых оераций
          var options = {
            day: "numeric",
            month: "long",
            year: "numeric",
          };
          console.log(item)
          var d = new Date(item.created_timestamp);
          const sumoperation = item.amount;
          let dataOperation = d.toLocaleString("ru", options);
          var num = +sumoperation;
          var result = num.toLocaleString();
          // враппер для коментария
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
            prevOperationComm.innerHTML = "Комментарий: " + comment;
          }
          st -= +sumoperation;
        });
        console.log(element)
        console.log(1111)
        DelOperationServise(element);

        // заполнение тайтла с результатом старых операций
        sumOperationEnded = st;
        var num = +st;
        var result = num.toLocaleString();

        const sumExpected = document.querySelector(".operation_entry_sum_all");
        sumExpected.innerHTML = result + " ₽";
        if (result == 0) {
          sumExpected.style.color = "black";
        }

        const sumChekedWrap = document.getElementById("sum_cheked");
        sumChekedWrap.setAttribute("data-step", "2");
        sumChekedWrap.innerHTML =
          '<h3>Сколько оплатили?</h3><div class="input_bank_wrap_add"><input checked type="radio" id="100" name="sum" value="' +
          sumOperationEnded +
          '" /><label for="100">Остаток</label><input type="radio" id="other_sum" name="sum" value="1" /><input placeholder="Другая сумма" data-validate="0" class = "pyb " type="text" id="other_sum_namber" name="" value="" /></div>';

        preloaderModal((isLoading = false), (isLoaded = true));
        // чекин другая сумма
        const chekinOtherSum = document.getElementById("other_sum_namber");
        chekinOtherSum.addEventListener("input", () => {
          const chekinOtherSum = document.getElementById("other_sum");
          replaceNam();
          chekinOtherSum.checked = true;
          return;
        });
      });
  } else {
    // если нет старых операций
    preloaderModal((isLoading = false), (isLoaded = true));
    const sumChekedWrap = document.getElementById("sum_cheked");
    sumChekedWrap.setAttribute("data-step", "1");
    sumChekedWrap.innerHTML =
      ' <h3>Сколько оплатили?</h3><div class="input_bank_wrap_add"><input  type="radio" id="100" name="sum" value="100" /><label for="100">100%</label><input type="radio" id="50" name="sum" value="50" /><label for="50">50%</label><input type="radio" id="other_sum" name="sum" value="1" /><input placeholder="Другая сумма" data-validate="0"  class = "pyb " type="text"  id="other_sum_namber" name="" value="" /></div>';

    const chekinOtherSum = document.getElementById("other_sum_namber");
    chekinOtherSum.addEventListener("input", () => {
      const chekinOtherSum = document.getElementById("other_sum");
      replaceNam();
      chekinOtherSum.checked = true;
    });
  }

  return idOperationrepl;
}
// удаление операции
function DelOperationServise(element) {
  console.log("DelOperation(element)")
  const delButton = document.querySelectorAll(".previous_operation_del");
  console.log("delButton")
  delButton.forEach((item) => {
    console.log(item)
    item.addEventListener("click", () => {
      idOperation = item.getAttribute("data-id-peration");
      let object = {
        "id": +idOperation,
      };

      const dataJson = JSON.stringify(object);
      preloaderModal((isLoading = true), (isLoaded = false));
      
      endpoint = "/api/v1/operation/operation_delete/";
      let csrfToken = getCookie("csrftoken");

      fetch(endpoint, {
        method: "POST",
        body: dataJson,
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
      }).then((response) => {
        if (response.ok === true) {
          console.log("getOldOperation")
          item.parentElement.remove();
          // заполнение инфом о операциях которые остались для повторого открытия окна с актцальными иоперациями
          // let operationIdvalue = element.getAttribute(
          //   "data-bill-month-operation-entry"
          // );
          // const idOperationrepl = operationIdvalue.replace(
          //   /^\D+|[^\d-]+|-(?=\D+)|\D+$/gim,
          //   ""
          // );
          // const idOperat = idOperationrepl.split("-");

          // let newidoper = "";
          // idOperat.forEach((item) => {
          //   if (item != idOperation) {
          //     newidoper += item + "-";
          //   }
          // });
          // element.setAttribute("data-bill-month-operation-entry", newidoper);

          const add_operation = document.querySelector(".operation_add");
          add_operation.replaceWith(add_operation.cloneNode(true));

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
