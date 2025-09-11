// replaceNamDot();
// const nalogBtn = document.querySelectorAll(".salary_employee_item_sum_nalog");
// if (nalogBtn) {
//   console.log(nalogBtn)
//   let old_elem;
//   let valueOld;
//   // console.log(old_elem)
//   nalogBtn.forEach((element) => {
//     element.addEventListener("click", (event) => {
//       console.log(element)
//       const elemValue = element.getAttribute("data-sum");
//       const salary_inp = element.querySelector(
//         ".salary_employee_item_sums_inp"
//       );
//       salary_inp.style.display = "block"
//       // salary_inp.previousElementSibling.style.display = "block"
//       const salary_text = element.querySelector(
//         ".salary_employee_item_sums_text"
//       );
//       salary_text.style.display = "None"

//       if (old_elem != element || old_elem == undefined) {
//         if (old_elem != undefined) {
     

//           old_elem.classList.remove("salary_employee_item_sum_nalog_active");
//           old_elem.readOnly = true;
//           old_elem.value = old_elem.getAttribute("data-sum");
//           const elemWrapOld = old_elem.parentNode;
//           const btnAddOld = elemWrapOld.querySelector(
//             ".btn_add_operation_nalog"
//           );
//           btnAddOld.classList.remove("salary_employee_item_sum_nalog_active");
//           old_elem.querySelector(
//             ".salary_employee_item_sums_text"
//           ).style.display = "block"
//           old_elem.querySelector(
//             ".salary_employee_item_sums_inp"
//           ).style.display = "none"
//         }

//         old_elem = element;

//         element.classList.add("salary_employee_item_sum_nalog_active");
//         element.readOnly = false;
//         element.value = "";
//         const elemWrap = element.parentNode;
//         const btnAdd = elemWrap.querySelector(".btn_add_operation_nalog");
//         replaceNamDot();

//         btnAdd.classList.add("salary_employee_item_sum_nalog_active");
//         NalogOperation(element, btnAdd);
//       }
//     });
//   });
// }

// function NalogOperation(element, btnAdd) {
// console.log("element,btnAdd")
//   console.log(element,btnAdd)
//   btnAdd.addEventListener("click", () => {
//     // function oldYearAccount(element) {
//     //   var now = new Date();
//     //   const operationYear = element.getAttribute("data-operation-data-year");
//     //   const operationMonth = element.getAttribute("data-operation-data-month");
//     //   const windowDate = new Date(operationYear, operationMonth, 1, 0, 0, 0, 0);
//     //   const jsonDate = windowDate.toJSON();
    
//     //   console.log(jsonDate);
    
//     //   return jsonDate;
//     // }
//     console.log(element);
//     var now = new Date();
//     const nowYear = now.getFullYear();
//     const nowMonth = now.getMonth() + 1;
//     const nowDay = now.getDate()
//     const actyalDateStr = nowYear + "-" + nowMonth + "-" + nowDay
//     console.log(now.toLocaleDateString())
//     let amount = element.querySelector(".salary_employee_item_sums_inp").value
//     const dataAmount = getCurrentPrice(amount)
//     console.log(dataAmount)
//     const dataId = element.getAttribute("data-operation-old-id");
//     const dataBank = element.getAttribute("data-bank-in");
//     const dataCAteg = element.getAttribute("data-categ-id");
//     const dataPeople = element.getAttribute("data-id-people");
//     const operationYears = element.getAttribute("data-operation-data-year");
//     const operationMonths = element.getAttribute("data-operation-data-month");
//     const operationYear = +operationYears;
//     const operationMonth = +operationMonths;
//     const startDate = element.getAttribute("data-operation-data-start-all_2");
//     const accountid = element.getAttribute("data-sub-categ-name");

//     const form = new FormData();
//     form.append("amount", dataAmount);
//     form.append("bank_to", 5);
//     form.append("bank_in", +dataBank);
//     form.append("employee", +dataPeople);
//     form.append("salary", accountid);
//     form.append("comment", "");
//     form.append("data", startDate);
    
    

    
    
    

//     // form.append("amount", dataAmount);
//     // form.append("bank", dataBank);
//     // form.append("category", dataCAteg);
//     // form.append("people", dataPeople);
//     // form.append("type_operation", "out");
//     // form.append("meta_categ", 'salary');
//     // form.append("data", actyalDateStr);

//     if (nowYear == operationYear && nowMonth == operationMonth) {
//     } else {
//       const oldDate = oldYearSalary(element);
//       // form.append("created_timestamp", oldDate);
//     }
//     let endpoint
//     let method 
//     if (dataId != "" & dataId != "None" & dataId != "{}"){
//       form.append("id", dataId);
//       endpoint = "/api-bookkeeping/v1/operation/" + dataId +"/"
//       method = "UPDATE"
//     } else {
//       endpoint = "/api-bookkeeping/v1/operation/operation_save/"
//       method = "POST"
//     }

//     let object = {};
//     form.forEach((value, key) => (object[key] = value));
//     const dataJson = JSON.stringify(object);

//     let csrfToken = getCookie("csrftoken");
    
//     fetch(endpoint, {
//       method: method,
//       body: dataJson,
//       headers: {
//         "Content-Type": "application/json",
//         "X-CSRFToken": csrfToken,
//       },
//     }).then((response) => {
//       if (response.ok === true) {
//        location.reload();
        
//       } else {
//         location.reload();
       
//       }
//     });
//   });

//   function oldYearSalary(element) {
//     var now = new Date();
//     const operationYear = element.getAttribute("data-operation-data-year");
//     const operationMonth = element.getAttribute("data-operation-data-month");
//     const windowDate = new Date(operationYear, operationMonth, 1, 0, 0, 0, 0);
//     const jsonDate = windowDate.toJSON();
  
//     console.log(jsonDate);
  
//     return jsonDate;
//   }
  
// }


// // // установка сортировки 

// // const sortDateSalary = document.querySelector(".salary-sorting");
// // if (sortDateSalary) {
// //   const sortMonthReload = sessionStorage.getItem("sortSalary");
// //   if (sortMonthReload) {
// //     sortDateSalary.setAttribute("salary-sorting-date", sortMonthReload);
// //   }

// //   const btnSort = document.querySelectorAll(".btn_sorting_salary");
// //   console.log(btnSort)
// //   btnSort.forEach((item) => {
// //     item.addEventListener("click", () => {
// //       const monthDate = item.getAttribute("data-sort-salary");
// //       sortDateSalary.setAttribute("data-sort-salary", monthDate);
// //       sessionStorage.setItem("sortSalary", monthDate);
// //       document.cookie = "sortSalary=" + monthDate;
// //       location.reload();
// //     });

// //     const indexBtn = sortDateSalary.getAttribute("salary-sorting-date");
// //     const monthDate = item.getAttribute("data-sort-salary");
// //     if (indexBtn == monthDate) {
// //       item.classList.add("active_sorting");
// //     }
// //   });
// // }
