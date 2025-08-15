replaceNamDot();
const salaryBtn = document.querySelectorAll(".inp_operation");
// Глобальная переменная для отслеживания активного элемента
let globalActiveElement = null;

if (salaryBtn) {
  console.log(salaryBtn);
  let old_elem;
  let valueOld;
  const pageName = document.getElementById("page_name").value;
  console.log("page_name", pageName);
  salaryBtn.forEach((element) => {
    element.addEventListener("click", (event) => {
      console.log(element);
      const elemValue = element.getAttribute("data-sum");
      const salary_inp = element.querySelector(
        ".salary_employee_item_sums_inp"
      );
      salary_inp.style.display = "block";
      // salary_inp.previousElementSibling.style.display = "block"
      const salary_text = element.querySelector(
        ".salary_employee_item_sums_text"
      );
      salary_text.style.display = "None";

      if (old_elem != element || old_elem == undefined) {
        // Деактивируем предыдущий элемент из этого блока
        if (old_elem != undefined) {
          console.log("old_elem!!!!!!!!!!!!!!!!!!!!!!!!!");
          old_elem.classList.remove("salary_employee_item_sums_active");
          old_elem.readOnly = true;
          old_elem.value = old_elem.getAttribute("data-sum");
          const elemWrapOld = old_elem.parentNode;
          const btnAddOld = elemWrapOld.querySelector(
            ".btn_add_operation_salary"
          );
          btnAddOld.classList.remove("btn_add_operation_salary_active");
          old_elem.querySelector(
            ".salary_employee_item_sums_text"
          ).style.display = "block";
          old_elem.querySelector(
            ".salary_employee_item_sums_inp"
          ).style.display = "none";
        }

        // Деактивируем элемент из другого блока, если он активен
        if (globalActiveElement && globalActiveElement !== element) {
          deactivateElement(globalActiveElement);
        }

        console.log("2222222222!!!!!!!!!!!!!!!!!!!!!!!!!");
        old_elem = element;
        globalActiveElement = element;

        element.classList.add("salary_employee_item_sums_active");
        element.readOnly = false;
        element.value = "";
        const elemWrap = element.parentNode;
        const btnAdd = elemWrap.querySelector(".btn_add_operation_salary");
        replaceNamDot();

        btnAdd.classList.add("btn_add_operation_salary_active");
        addSalaryOperation(element, btnAdd, pageName);
      }
    });
  });
}

function addSalaryOperation(element, btnAdd, pageName) {
  console.log(element);
  document.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
      // Проверяем, была ли нажата клавиша Enter
      btnAdd.click(); // Имитируем нажатие на кнопку
    }
  });
  btnAdd.addEventListener("click", () => {
    const form = new FormData();
    console.log(element);
    if (pageName == "Налоги") {
      form.append("bank_to", 5);
      const accountid = element.getAttribute("data-sub-categ-name");
      form.append("nalog", accountid);
    } else if (pageName == "Зарплата") {
      const dataPeople = element.getAttribute("data-id-people");
      form.append("employee", +dataPeople);
      form.append("bank_to", 5);
      const accountid = element.getAttribute("data-sub-categ-name");
      form.append("salary", accountid);
    } else if (pageName == "OOO") {
      const bank_to = element.getAttribute("data-bank-out");
      form.append("bank_to", bank_to);
      const type = element.getAttribute("tupe-operations");
      if (type == "between") {
        form.append("bank_in", 1);
        betweenId = element.getAttribute("data-between-id");
        console.log(element);
        console.log(betweenId);
        form.append("between_bank", betweenId);
      } else if (type == "percent") {
      } else if (type == "SubcontractOtherCategory") {
        const categId = element.getAttribute("data-sub-categ-id");
        form.append("bank_in", 1);
        form.append("suborder_other", categId);
      } else if (type == "nalog") {
        form.append("bank_to", 5);
        const accountid = element.getAttribute("data-sub-categ-id");
        form.append("nalog", accountid);
      } else {
      }
    } else if (pageName == "ИП") {
      const bank_to = element.getAttribute("data-bank-out");
      form.append("bank_to", bank_to);
      const type = element.getAttribute("tupe-operations");
      if (type == "between") {
        form.append("bank_in", 1);
        betweenId = element.getAttribute("data-between-id");
        console.log(element);
        console.log(betweenId);
        form.append("between_bank", betweenId);
      } else if (type == "percent") {
      } else if (type == "SubcontractOtherCategory") {
        const categId = element.getAttribute("data-sub-categ-id");
        form.append("bank_in", 1);
        form.append("suborder_other", categId);
      } else if (type == "nalog") {
        form.append("bank_to", 5);
        const accountid = element.getAttribute("data-sub-categ-id");
        form.append("nalog", accountid);
      } else {
      }
    } else if (pageName == "$") {
      const bank_to = element.getAttribute("data-bank-out");
      form.append("bank_to", bank_to);
      const type = element.getAttribute("tupe-operations");
      if (type == "between") {
        form.append("bank_in", 1);
        betweenId = element.getAttribute("data-between-id");
        console.log(element);
        console.log(betweenId);
        form.append("between_bank", betweenId);
      } else if (type == "percent") {
      } else if (type == "SubcontractOtherCategory") {
        const categId = element.getAttribute("data-sub-categ-id");
        form.append("bank_in", 1);
        form.append("suborder_other", categId);
      } else if (type == "nalog") {
        form.append("bank_to", 5);
        const accountid = element.getAttribute("data-sub-categ-id");
        form.append("nalog", accountid);
      } else {
      }
    }
    else if (pageName == "Накопительные счета") {
      const bank_to = element.getAttribute("data-bank-out");
      form.append("bank_to", bank_to);
      const type = element.getAttribute("tupe-operations");
      if (type == "between") {
        form.append("bank_in", 1);
        betweenId = element.getAttribute("data-between-id");
        console.log(element);
        console.log(betweenId);
        form.append("between_bank", betweenId);
      } else if (type == "percent") {
      } else if (type == "SubcontractOtherCategory") {
        const categId = element.getAttribute("data-sub-categ-id");
        form.append("bank_in", 1);
        form.append("suborder_other", categId);
      } else if (type == "nalog") {
        form.append("bank_to", 5);
        const accountid = element.getAttribute("data-sub-categ-id");
        form.append("nalog", accountid);
      } else {
        form.append("bank_to", 5);
        const accountid = element.getAttribute("data-sub-categ-id");
      }
    }
    var now = new Date();
    const nowYear = now.getFullYear();
    const nowMonth = now.getMonth() + 1;
    const nowDay = now.getDate();
    const actyalDateStr = nowYear + "-" + nowMonth + "-" + nowDay;
    console.log(now.toLocaleDateString());
    let amount = element.querySelector(".salary_employee_item_sums_inp").value;
    const dataAmount = getCurrentPrice(amount);
    console.log(dataAmount);
    const dataId = element.getAttribute("data-operation-old-id");
    const dataBank = element.getAttribute("data-bank-in");
    const dataCAteg = element.getAttribute("data-categ-id");

    const operationYears = element.getAttribute("data-operation-data-year");
    const operationMonths = element.getAttribute("data-operation-data-month");
    const operationYear = +operationYears;
    const operationMonth = +operationMonths;
    const startDate = element.getAttribute("data-operation-data-start-all_2");

    form.append("amount", dataAmount);

    form.append("bank_in", +dataBank);

    form.append("comment", "");
    form.append("data", startDate);

    if (nowYear == operationYear && nowMonth == operationMonth) {
    } else {
      const oldDate = oldYearSalary(element);
      // form.append("created_timestamp", oldDate);
    }
    let endpoint;
    let method;
    if (
      (dataId != "") &
      (dataId != "None") &
      (dataId != "{}") &
      (dataId != 0)
    ) {
      if (dataAmount == 0) {
        form.append("id", dataId);
        endpoint = "/api/v1/operation/" + dataId + "/";
        method = "DELETE";
      } else {
        form.append("id", dataId);
        endpoint = "/api/v1/operation/" + dataId + "/";
        method = "UPDATE";
      }
    } else {
      endpoint = "/api/v1/operation/operation_save/";
      method = "POST";
    }

    let object = {};
    form.forEach((value, key) => (object[key] = value));
    const dataJson = JSON.stringify(object);
    console.log(dataJson);
    let csrfToken = getCookie("csrftoken");

    fetch(endpoint, {
      method: method,
      body: dataJson,
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
    }).then((response) => {
      if (response.ok === true) {
        location.reload();
      } else {
        const errorModal = document.getElementById("modal-error");
        errorModal.classList.add("modal-active");
        const error_modal_text = errorModal.querySelector(".error_modal_text");
        error_modal_text.textContent = "Ошибка при сохранении операции - " + response.status + " " + response.detail;
        // location.reload();
      }
    });
  });

  function oldYearSalary(element) {
    var now = new Date();
    const operationYear = element.getAttribute("data-operation-data-year");
    const operationMonth = element.getAttribute("data-operation-data-month");
    const windowDate = new Date(operationYear, operationMonth, 1, 0, 0, 0, 0);
    const jsonDate = windowDate.toJSON();

    console.log(jsonDate);

    return jsonDate;
  }
}

// Функция для деактивации элемента
function deactivateElement(element) {
  if (element.classList.contains("salary_employee_item_sums_active")) {
    element.classList.remove("salary_employee_item_sums_active");
    element.readOnly = true;
    element.value = element.getAttribute("data-sum");
    
    const elemWrap = element.parentNode;
    const btnAdd = elemWrap.querySelector(".btn_add_operation_salary");
    if (btnAdd) {
      btnAdd.classList.remove("btn_add_operation_salary_active");
    }
    
    const salaryText = element.querySelector(".salary_employee_item_sums_text");
    const salaryInp = element.querySelector(".salary_employee_item_sums_inp");
    
    if (salaryText) salaryText.style.display = "block";
    if (salaryInp) salaryInp.style.display = "none";
  }
}

const salaryBtnPercent = document.querySelectorAll(".inp_operation_percent");
if (salaryBtnPercent) {
  console.log(salaryBtnPercent);
  let old_elem;
  let valueOld;
  const pageName = document.getElementById("page_name").value;
  console.log("page_name", pageName);
  salaryBtnPercent.forEach((element) => {
    element.addEventListener("click", (event) => {
      const checkPersentRate = document.querySelectorAll(".check-persent");
      console.log("checkPersentRate", checkPersentRate);
      if (checkPersentRate.length > 0) {
        // checkPersentRate(element)
      }
      console.log(element);
      const elemValue = element.getAttribute("data-sum");
      const salary_inp = element.querySelector(
        ".salary_employee_item_sums_inp"
      );
      salary_inp.style.display = "block";
      // salary_inp.previousElementSibling.style.display = "block"
      const salary_text = element.querySelector(
        ".salary_employee_item_sums_text"
      );
      salary_text.style.display = "None";

      if (old_elem != element || old_elem == undefined) {
        // Деактивируем предыдущий элемент из этого блока
        if (old_elem != undefined) {
          old_elem.classList.remove("salary_employee_item_sums_active");
          old_elem.readOnly = true;
          old_elem.value = old_elem.getAttribute("data-sum");
          const elemWrapOld = old_elem.parentNode;
          const btnAddOld = elemWrapOld.querySelector(
            ".btn_add_operation_salary"
          );
          btnAddOld.classList.remove("btn_add_operation_salary_active");
          old_elem.querySelector(
            ".salary_employee_item_sums_text"
          ).style.display = "block";
          old_elem.querySelector(
            ".salary_employee_item_sums_inp"
          ).style.display = "none";
        }

        // Деактивируем элемент из другого блока, если он активен
        if (globalActiveElement && globalActiveElement !== element) {
          deactivateElement(globalActiveElement);
        }

        old_elem = element;
        globalActiveElement = element;

        element.classList.add("salary_employee_item_sums_active");
        element.readOnly = false;
        element.value = "";
        const elemWrap = element.parentNode;
        const btnAdd = elemWrap.querySelector(".btn_add_operation_salary");
        replaceNamDot();

        btnAdd.classList.add("btn_add_operation_salary_active");
        addSalaryOperationPercent(element, btnAdd, pageName);
      }
    });
  });
}

function addSalaryOperationPercent(element, btnAdd, pageName) {
  console.log(element);
  document.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
      // Проверяем, была ли нажата клавиша Enter
      btnAdd.click(); // Имитируем нажатие на кнопку
    }
  });
  btnAdd.addEventListener("click", () => {
    const form = new FormData();

    const dataId = element.getAttribute("data-operation-old-id");
    const startDate = element.getAttribute("data-operation-data-start-all_2");

    form.append("data", startDate);

    let amount = element.querySelector(".salary_employee_item_sums_inp").value;
    const dataAmount = getCurrentPrice(amount);
    form.append("percent", dataAmount);
    const categId = element.getAttribute("data-sub-categ-id");
    form.append("category", categId);
    const dataBetweenId = element.getAttribute("data-between-id");
    if (dataBetweenId != "") {
      form.append("category", categId);
    }
    const dataSubcategName = element.getAttribute("data-sub-categ-name");
    if (dataSubcategName == "employee") {
      const dataEmployee = element.getAttribute("data-id-people");
      form.append("employee", +dataEmployee);
      if (
        (dataId != "") &
        (dataId != "None") &
        (dataId != "{}") &
        (dataId != 0)
      ) {
        form.append("id", dataId);
        endpoint = "/api/v1/percentemployee/" + dataId + "/";
        method = "UPDATE";
      } else {
        endpoint = "/api/v1/percentemployee/";
        method = "POST";
      }
    }
    else {
      if (
        (dataId != "") &
        (dataId != "None") &
        (dataId != "{}") &
        (dataId != 0)
      ) {
        form.append("id", dataId);
        endpoint = "/api/v1/percentgroupbank/" + dataId + "/";
        method = "UPDATE";
      } else {
        endpoint = "/api/v1/percentgroupbank/";
        method = "POST";
      }
    }



    let object = {};
    form.forEach((value, key) => (object[key] = value));
    const dataJson = JSON.stringify(object);
    console.log(dataJson);
    let csrfToken = getCookie("csrftoken");

    fetch(endpoint, {
      method: method,
      body: dataJson,
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
    }).then((response) => {
      if (response.ok === true) {
        location.reload();
      } else {
        // location.reload();
      }
    });
  });
}

const chakboxInp = document.querySelectorAll(".checkbox-persent");
if (chakboxInp) {
  chakboxInp.forEach((element) => {
    console.log(chakboxInp);
    element.addEventListener("click", (event) => {
      const form = new FormData();

      const dataId = element.getAttribute("data-operation-old-id");
      const startDate = element.getAttribute("data-operation-data-start-all_2");
      const summOper = element.getAttribute("data-summ");

      form.append("data", startDate);
      const dataAmount = getCurrentPrice(summOper);
      form.append("amount", dataAmount);
      const dataBank = element.getAttribute("data-bank-in");
      if (dataBank !== "NONE_OPERATION") {
        form.append("bank_in", +dataBank);
        betweenId = element.getAttribute("data-between-id");
        if (betweenId !== "None" && betweenId !== "" && betweenId !== "{}" && betweenId !== "0") {
          console.log(element);
          console.log(betweenId);
          form.append("between_bank", betweenId);
        } else {
          const dataPeople = element.getAttribute("data-id-people");
          form.append("employee", +dataPeople);
          const accountid = element.getAttribute("data-sub-categ-name");
          form.append("salary", accountid);
        }
        const bank_to = element.getAttribute("data-bank-out");
        form.append("bank_to", bank_to);

        let endpoint;
        let method;
        if (element.checked) {
          // Чекбокс установлен (нажат)
          console.log("Чекбокс нажат");
          if (
            (dataId != "") &
            (dataId != "None") &
            (dataId != "{}") &
            (dataId != 0)
          ) {
            form.append("id", dataId);
            endpoint = "/api/v1/operation/" + dataId + "/";
            method = "UPDATE";
          } else {
            endpoint = "/api/v1/operation/operation_save/";
            method = "POST";
          }
        } else {
          // Чекбокс снят (отжат)
          console.log("Чекбокс снят");
          if (
            (dataId != "") &
            (dataId != "None") &
            (dataId != "{}") &
            (dataId != 0)
          ) {
            form.append("id", dataId);
            endpoint = "/api/v1/operation/" + dataId + "/";
            method = "DELETE";
          } else {
            endpoint = "/api/v1/operation/operation_save/";
            method = "POST";
          }
        }

        let object = {};
        form.forEach((value, key) => (object[key] = value));
        const dataJson = JSON.stringify(object);
        console.log(dataJson);
        let csrfToken = getCookie("csrftoken");
        console.log(betweenId);
        if (betweenId !== "NONE_OPERATION") {
          fetch(endpoint, {
            method: method,
            body: dataJson,
            headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": csrfToken,
            },
          }).then((response) => {
            if (response.ok === true) {
              location.reload();
            } else {
              // location.reload();
            }
          });
        }
      }
    });
  });
}


// const checkPersentRate = document.querySelectorAll(".check-persent");

// if(checkPersentRate){
//   checkPersentRate(element)
// }

function checkPersentRate(element) {
  const dataOperationMonth = element.getAttribute("data-operation-data-month");
  const dataOperationSubcategId = element.getAttribute("data-sub-categ-id");
  const parentSection = element.closest(".section_oper_wr");
  const persentSummElem = parentSection
    ? parentSection.querySelector(
      `[data-month="${dataOperationMonth}"][data-sub-categ-name="${dataOperationSubcategId}"]`
    )
    : null;
  const persentSumm = persentSummElem.getAttribute("data-persent-use");
  console.log(persentSumm);
  element.addEventListener("input", (event) => {

  })
}