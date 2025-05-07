const addOperationOperAccount = document.querySelectorAll(
  ".add_operation_oper_account"
);

if (addOperationOperAccount) {
  addOperationOperAccount.forEach((element) => {
    element.addEventListener("click", () => {
      document.getElementById("date-operation_operacc").valueAsDate =
        new Date();
      const lastOperationWrap = document.querySelector(
        ".previous_operation_oper_acc"
      );
      lastOperationWrap.innerHTML = "";

      const add_operation = document.querySelector(
        ".add_operation_oper_account_btn"
      );
      let elem = element.getAttribute("data-name");
      //   add_operation.disabled = true;

      modal(elem, add_operation);
      preloaderModal((isLoading = true), (isLoaded = false));
      getInfoOperAccountOperation(element);
      getSumOldOperAccountOperation(element, elem);
      addFethOperationOperAcc(element, elem);
      // валидация радиокнопок
      const modalWindows = document.getElementById(elem);
      modalWindows.addEventListener("input", () => {
        validateRadio(
          elem,
          ".add_operation_oper_account_btn",
          ".input_bank_wrap_operacc",
          ".input_bank_wrap_oper_account"
        );
      });
      oldYearOperAccount(element, elem);
    });
  });
}

// заполнение тайтла инфой
function getInfoOperAccountOperation(element) {
  const categName = element.getAttribute("data-categ-name");
  const subCategName = element.getAttribute("data-sub-categ-name");
  const subCategSum = element.getAttribute("data-operation-sum");
  const dataName = element.getAttribute("data-operation-data");

  const modalcategName = document.querySelector(".oper_account_title_categ");
  const modalsubCategName = document.querySelector(
    ".oper_account_title_sub_categ"
  );
  const modalsubCategSum = document.querySelector(
    ".oper_account_title_sub_categ_sum"
  );
  const modaldataName = document.querySelector(".oper_account_period_data");

  modalcategName.innerHTML = categName;
  modalsubCategName.innerHTML = subCategName + ":";
  modalsubCategSum.innerHTML = subCategSum + " ₽";
  modaldataName.innerHTML = dataName;
}

function getSumOldOperAccountOperation(element, elem) {
  function getArrOldOper(element) {
    // let operationAllSum = element.getAttribute(
    //   "data-operation-sum"
    // );
    // let st = parseInt(operationAllSum.replace(/\s+/g, ""), 10);

    let operationIdvalue = element.getAttribute("data-operation-old-id");
    const idOperationrepl = operationIdvalue.replace(
      /^\D+|[^\d-]+|-(?=\D+)|\D+$/gim,
      ""
    );
    const idOperation = idOperationrepl.split("-");
    let json;
    if (idOperationrepl !== "") {
      let old_oper = [];
      const sumcheked = document.querySelector(".sum_cheked");
      idOperation.forEach((item) => {
        const Obj = {
          id: item,
        };
        old_oper.push(Obj);
      });

      json = JSON.stringify(old_oper);
    }
    return json;
  }

  const old_operat = getArrOldOper(element);

  const month = element.getAttribute("data-operation-data-month");
  const year = element.getAttribute("data-operation-data-year");
  const categNameId = element.getAttribute("data-categ-id");
  const bankElem = document.querySelector(".oper_account_sort_bank-active");
  let bank;
  if (bankElem) {
    bank = bankElem.getAttribute("data-sort-operation");
  } else {
    bank = "0";
  }

  const form = new FormData();
  form.append("month", month);
  form.append("year", year);
  form.append("categ_id", categNameId);
  form.append("bank", bank);

  let object = {};
  form.forEach((value, key) => (object[key] = value));
  const dataJson = JSON.stringify(object);

  let csrfToken = getCookie("csrftoken");

  fetch("/operations/api/operation/operation_oper_account/", {
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
        let total = 0;
        data.forEach((item) => {
          total += item["total"];
        });

        var num = +total;
        var result = num.toLocaleString();
        const inputSumWrap = document.querySelector(
          ".input_bank_wrap_oper_account"
        );
        inputSumWrap.innerHTML =
          '<input type="radio" id="sum_out_oper_account" name="sum" value="' +
          total +
          '"/><label for="sum_out_oper_account">' +
          result +
          " ₽" +
          '</label> <input type="radio" id="other_sum_out_oper_account" name="sum" value="1" /><input data-validate="0" type="text" class = "pyb" id="other_sum_namber_oper_account"value=""placeholder="Cумма" />';
      } else {
        const inputSumWrap = document.querySelector(
          ".input_bank_wrap_oper_account"
        );
        inputSumWrap.innerHTML =
          '<input type="radio" id="other_sum_out_oper_account" name="sum" value="1" /><input data-validate="0" type="text" class = "pyb" id="other_sum_namber_oper_account"value=""placeholder="Cумма" />';
      }

      // чекин другая сумма
      const chekinOtherSum = document.getElementById(
        "other_sum_namber_oper_account"
      );
      chekinOtherSum.addEventListener("input", () => {
        const chekinOtherSum = document.getElementById(
          "other_sum_out_oper_account"
        );
        replaceNam();
        chekinOtherSum.checked = true;
        return;
      });
      return;
    })
    .then(() => {
      fetch("/operations/api/operation/operation_entry_list/", {
        method: "POST",
        body: old_operat,
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
      })
        .then((response) => response.json())
        .then((data) => {
          let operationAllSum = element.getAttribute("data-operation-sum");
          let st = 0;
          // let st = parseInt(operationAllSum.replace(/\s+/g, ""), 10);
          console.log("st",st);
          if (data.length > -1) {
            const lastOperationWrap = document.querySelector(
              ".previous_operation_oper_acc"
            );
            lastOperationWrap.innerHTML = "";
            console.log("data",data)
            data.forEach((item) => {
              // полученые старых оераций
              var options = {
                day: "numeric",
                month: "long",
                year: "numeric",
              };
              var d = new Date(item[0].created_timestamp);
              const sumoperation = item[0].amount;
              let dataOperation = d.toLocaleString("ru", options);
              var num = +sumoperation;
              var result = num.toLocaleString();
              // враппер для коментария
              let prevOperationItem = document.createElement("div");
              prevOperationItem.className = "previous_operation_item";
              lastOperationWrap.append(prevOperationItem);
              // кнопка удалить
              let prevOperationDel = document.createElement("div");
              prevOperationDel.className = "previous_operation_del_oper";
              prevOperationItem.append(prevOperationDel);
              prevOperationDel.setAttribute("data-id-peration", item[0].id);
              prevOperationDel.innerHTML = "+";

              let prevOperationiNoComm = document.createElement("div");
              prevOperationiNoComm.className = "previous_operation_wrap";
              prevOperationItem.append(prevOperationiNoComm);

              let prevOperationTitle = document.createElement("div");
              prevOperationTitle.className = "previous_operation_title";
              prevOperationiNoComm.append(prevOperationTitle);
              prevOperationTitle.innerHTML =
                dataOperation + " - оплата " + result + " ₽ ";

              let comment = item[0].comment;

              let prevOperationComm = document.createElement("div");
              prevOperationComm.className = "previous_operation_comment";
              prevOperationiNoComm.append(prevOperationComm);
              if (comment != null && comment != "") {
                prevOperationComm.innerHTML = "Комментарий: " + comment;
              }
              console.log(sumoperation);
              st += +sumoperation;
            });
            DelOperation(element);
            console.log(st);
            // заполнение тайтла с результатом старых операций
            sumOperationEnded = st;
            console.log("sumOperationEnded",sumOperationEnded)
            var num = +st;
            console.log("num",num)

            var result = num.toLocaleString();
            console.log("result",result)
            const sumExpected = document.querySelector(
              ".oper_account_title_sub_categ_sum"
            );
            sumExpected.innerHTML = result + " ₽";
          }
          preloaderModal((isLoading = false), (isLoaded = true));
        });
    });
}

function DelOperation(element) {
  const delButton = document.querySelectorAll(".previous_operation_del_oper");
  delButton.forEach((item) => {
    item.addEventListener("click", () => {
      preloaderModal((isLoading = true), (isLoaded = false));
      idOperation = item.getAttribute("data-id-peration");
      endpoint = "/operations/api/operation/" + idOperation + "/";

      fetch(endpoint, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
        },
      }).then((response) => {
        if (response.ok === true) {
          console.log("getOldOperationOPERACCOUNT")
          item.parentElement.remove();
          
          // заполнение инфом о операциях которые остались для повторого открытия окна с актцальными иоперациями
          let operationIdvalue = element.getAttribute("data-operation-old-id");
          const idOperationrepl = operationIdvalue.replace(
            /^\D+|[^\d-]+|-(?=\D+)|\D+$/gim,
            ""
          );
          const idOperat = idOperationrepl.split("-");

          let newidoper = "";
          idOperat.forEach((item) => {
            if (item != idOperation) {
              newidoper += item + "-";
            }
          });
          element.setAttribute("data-operation-old-id", newidoper);

          const add_operation = document.querySelector(
            ".add_operation_oper_account_btn "
          );
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

function addFethOperationOperAcc(element, elem) {
  const btnAddOperationEntry = document.querySelector(
    ".add_operation_oper_account_btn"
  );
  btnAddOperationEntry.addEventListener("click", () => {
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
    const sumElement = document.querySelectorAll(
      '#sum_cheked_out_oper_account input[name="sum"]'
    );
    sumElement.forEach((el) => {
      if (el.checked) {
        if (el.value > "1") {
          sumChecked = +el.value;

          return;
        } else {
          const otherSumCheck = document.querySelector(
            "#other_sum_namber_oper_account"
          );
          sumChecked = +otherSumCheck.value
            .replace(/[^+\d]/g, "")
            .replace(/(\d)\++/g, "$1");
          return;
        }
      }
    });

    const commentOperation = document.getElementById("operation_comment").value;
    const data_select = document.getElementById("date-operation_operacc").value;
    const categ = element.getAttribute("data-categ-id");
    const form = new FormData();
    form.append("amount", sumChecked);
    form.append("comment", commentOperation);
    form.append("bank", bankChecked);
    form.append("type_operation", "out");
    form.append("meta_categ", "oper_account");
    // form.append("meta_category", "4");
    form.append("category", categ);
    form.append("data", data_select);

    var now = new Date();
    const operationYears = element.getAttribute("data-operation-data-year");
    const operationMonths = element.getAttribute("data-operation-data-month");
    const operationYear = +operationYears;
    const operationMonth = +operationMonths;
    const nowYear = now.getFullYear();
    const nowMonth = now.getMonth() + 1;
    if (nowYear == operationYear && nowMonth == operationMonth) {
    } else {
      const oldDate = oldYearOperAccount(element);
      form.append("created_timestamp", oldDate);
    }


    let object = {};
    form.forEach((value, key) => (object[key] = value));
    const dataJson = JSON.stringify(object);

    let csrfToken = getCookie("csrftoken");
    fetch("/operations/api/operation/", {
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

function oldYearOperAccount(element) {
  var now = new Date();
  const operationYear = element.getAttribute("data-operation-data-year");
  const operationMonth = element.getAttribute("data-operation-data-month");
  const windowDate = new Date(operationYear, operationMonth, 1, 0, 0, 0, 0);
  const jsonDate = windowDate.toJSON();

  console.log(jsonDate);

  return jsonDate;
}
