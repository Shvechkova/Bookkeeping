replaceNamDot();
const salaryBtn = document.querySelectorAll(".inp_operation");
if (salaryBtn) {
  console.log(salaryBtn)
  let old_elem;
  let valueOld;
    const pageName = document.getElementById('page_name').value
  console.log("page_name", pageName)
  salaryBtn.forEach((element) => {
    element.addEventListener("click", (event) => {
      console.log(element)
      const elemValue = element.getAttribute("data-sum");
      const salary_inp = element.querySelector(
        ".salary_employee_item_sums_inp"
      );
      salary_inp.style.display = "block"
      // salary_inp.previousElementSibling.style.display = "block"
      const salary_text = element.querySelector(
        ".salary_employee_item_sums_text"
      );
      salary_text.style.display = "None"

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
          old_elem.querySelector(
            ".salary_employee_item_sums_text"
          ).style.display = "block"
          old_elem.querySelector(
            ".salary_employee_item_sums_inp"
          ).style.display = "none"
        }

        old_elem = element;

        element.classList.add("salary_employee_item_sums_active");
        element.readOnly = false;
        element.value = "";
        const elemWrap = element.parentNode;
        const btnAdd = elemWrap.querySelector(".btn_add_operation_salary");
        replaceNamDot();

        btnAdd.classList.add("btn_add_operation_salary_active");
        addSalaryOperation(element, btnAdd,pageName);
      }
    });
  });
}

function addSalaryOperation(element, btnAdd,pageName) {
  console.log(element)
  document.addEventListener('keydown', function(event) {
    if (event.key === 'Enter') { // Проверяем, была ли нажата клавиша Enter
      btnAdd.click(); // Имитируем нажатие на кнопку
    }
  });
  btnAdd.addEventListener("click", () => {
    const form = new FormData();
    console.log(element);
    if (pageName == "Налоги"){
        form.append("bank_to", 5);
        const accountid = element.getAttribute("data-sub-categ-name");
        form.append("nalog", accountid);
    }else if(pageName == "salary"){
        const dataPeople = element.getAttribute("data-id-people");
        form.append("employee", +dataPeople);
        form.append("bank_to", 5);
        const accountid = element.getAttribute("data-sub-categ-name");
        form.append("salary", accountid);
    }
    else if(pageName == "OOO"){
      const bank_to = element.getAttribute("data-bank-out");
      form.append("bank_to", bank_to);
      const type = element.getAttribute("tupe-operations");
      if (type == "between"){
        form.append("bank_in", 1);
        betweenId = element.getAttribute("data-between-id");
        console.log(element)
        console.log(betweenId)
        form.append("between_bank", betweenId);
      }
      else if(type == "percent"){
        
      }
      else if(type == "SubcontractOtherCategory"){
        const categId = element.getAttribute("data-sub-categ-id");
        form.append("bank_in", 1);
        form.append("suborder_other", categId);
      }
      else{
        
      }
      
  }
    var now = new Date();
    const nowYear = now.getFullYear();
    const nowMonth = now.getMonth() + 1;
    const nowDay = now.getDate()
    const actyalDateStr = nowYear + "-" + nowMonth + "-" + nowDay
    console.log(now.toLocaleDateString())
    let amount = element.querySelector(".salary_employee_item_sums_inp").value
    const dataAmount = getCurrentPrice(amount)
    console.log(dataAmount)
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
    let endpoint
    let method 
    if (dataId != "" & dataId != "None" & dataId != "{}" & dataId != 0){
      form.append("id", dataId);
      endpoint = "/api/v1/operation/" + dataId +"/"
      method = "UPDATE"
    } else {
      endpoint = "/api/v1/operation/operation_save/"
      method = "POST"
    }

    let object = {};
    form.forEach((value, key) => (object[key] = value));
    const dataJson = JSON.stringify(object);
    console.log(dataJson)
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

const salaryBtnPercent = document.querySelectorAll(".inp_operation_percent");
if (salaryBtnPercent) {
  console.log(salaryBtnPercent)
  let old_elem;
  let valueOld;
    const pageName = document.getElementById('page_name').value
  console.log("page_name", pageName)
  salaryBtnPercent.forEach((element) => {
    element.addEventListener("click", (event) => {
      console.log(element)
      const elemValue = element.getAttribute("data-sum");
      const salary_inp = element.querySelector(
        ".salary_employee_item_sums_inp"
      );
      salary_inp.style.display = "block"
      // salary_inp.previousElementSibling.style.display = "block"
      const salary_text = element.querySelector(
        ".salary_employee_item_sums_text"
      );
      salary_text.style.display = "None"

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
          old_elem.querySelector(
            ".salary_employee_item_sums_text"
          ).style.display = "block"
          old_elem.querySelector(
            ".salary_employee_item_sums_inp"
          ).style.display = "none"
        }

        old_elem = element;

        element.classList.add("salary_employee_item_sums_active");
        element.readOnly = false;
        element.value = "";
        const elemWrap = element.parentNode;
        const btnAdd = elemWrap.querySelector(".btn_add_operation_salary");
        replaceNamDot();

        btnAdd.classList.add("btn_add_operation_salary_active");
        addSalaryOperationPercent(element, btnAdd,pageName);
      }
    });
  });
}

function addSalaryOperationPercent(element, btnAdd,pageName) {
  console.log(element)
  document.addEventListener('keydown', function(event) {
    if (event.key === 'Enter') { // Проверяем, была ли нажата клавиша Enter
      btnAdd.click(); // Имитируем нажатие на кнопку
    }
  });
  btnAdd.addEventListener("click", () => {
    const form = new FormData();

    const dataId = element.getAttribute("data-operation-old-id");
    const startDate = element.getAttribute("data-operation-data-start-all_2");


    form.append("data", startDate);
    
    let amount = element.querySelector(".salary_employee_item_sums_inp").value
    const dataAmount = getCurrentPrice(amount)
    form.append("percent", dataAmount);
    const categId = element.getAttribute("data-sub-categ-id");
    form.append("category", categId);


    if (dataId != "" & dataId != "None" & dataId != "{}" & dataId != 0){
      form.append("id", dataId);
      endpoint = "/api/v1/percentgroupbank/" + dataId +"/"
      method = "UPDATE"
    } else {
      endpoint = "/api/v1/percentgroupbank/"
      method = "POST"
    }

    let object = {};
    form.forEach((value, key) => (object[key] = value));
    const dataJson = JSON.stringify(object);
    console.log(dataJson)
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