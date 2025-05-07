replaceNamDot();
const salaryBtn = document.querySelectorAll(".salary_employee_item_sums");
if (salaryBtn) {
  let old_elem;
  let valueOld;
  // console.log(old_elem)
  salaryBtn.forEach((element) => {
    element.addEventListener("click", (event) => {
      const elemValue = element.getAttribute("data-sum");

      if (old_elem != element || old_elem == undefined) {
        if (old_elem != undefined) {
     

          old_elem.classList.remove("salary_employee_item_sums_active");
          old_elem.readOnly = true;
          old_elem.value = old_elem.getAttribute("data-sum");
          const elemWrapOld = old_elem.parentNode;
          const btnAddOld = elemWrapOld.querySelector(
            ".btn_add_operation_salary"
          );
          btnAddOld.classList.remove("btn_add_operation_salary_active");
        }

        old_elem = element;

        element.classList.add("salary_employee_item_sums_active");
        element.readOnly = false;
        element.value = "";
        const elemWrap = element.parentNode;
        const btnAdd = elemWrap.querySelector(".btn_add_operation_salary");
        replaceNamDot();

        btnAdd.classList.add("btn_add_operation_salary_active");
        addSalaryOperation(element, btnAdd);
      }
    });
  });
}

function addSalaryOperation(element, btnAdd) {
  btnAdd.addEventListener("click", () => {
    console.log(element);
    var now = new Date();
    const nowYear = now.getFullYear();
    const nowMonth = now.getMonth() + 1;
    const nowDay = now.getDate()
    const actyalDateStr = nowYear + "-" + nowMonth + "-" + nowDay
    console.log(now.toLocaleDateString())
    const dataAmount = element.value .replace(/[^+\d]/g, "")
    .replace(/(\d)\++/g, "$1");
    console.log(dataAmount)
    const dataId = element.getAttribute("data-operation-old-id");
    const dataBank = element.getAttribute("data-bank");
    const dataCAteg = element.getAttribute("data-categ-id");
    const dataPeople = element.getAttribute("data-id-people");
    const operationYears = element.getAttribute("data-operation-data-year");
    const operationMonths = element.getAttribute("data-operation-data-month");
    const operationYear = +operationYears;
    const operationMonth = +operationMonths;
    
  

    const form = new FormData();
    form.append("amount", dataAmount);
    form.append("bank", dataBank);
    form.append("category", dataCAteg);
    form.append("people", dataPeople);
    form.append("type_operation", "out");
    form.append("meta_categ", 'salary');
    form.append("data", actyalDateStr);

    if (nowYear == operationYear && nowMonth == operationMonth) {
    } else {
      const oldDate = oldYearSalary(element);
      form.append("created_timestamp", oldDate);
    }
    let endpoint
    let method 
    if (dataId != ""){
      form.append("id", dataId);
      endpoint = "/operations/api/operation/" + dataId +"/"
      method = "UPDATE"
    } else {
      endpoint = "/operations/api/operation/"
      method = "POST"
    }

    let object = {};
    form.forEach((value, key) => (object[key] = value));
    const dataJson = JSON.stringify(object);

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
        location.reload();
       
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
