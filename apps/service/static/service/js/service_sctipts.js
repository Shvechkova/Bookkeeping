//новый месяц кнопка
const newBillMonth = document.querySelector(".new_month");
if (newBillMonth) {
  newBillMonth.addEventListener("click", () => {
    location.href = window.location.origin + "/service/new_month";
    window.history.back();
  });
}


// // установка сортировки operation
const sortOper = document.querySelector(".bill-sorting-operation");
if (sortOper) {
  const sortOperReload = sessionStorage.getItem("sortOper");
  const btnSortOper = document.querySelectorAll(".btn_sorting_operation");

  if (sortOperReload) {
    sortOper.setAttribute("bill-sorting-oper", sortOperReload);
  } else {
    document.cookie = "sortOper=" + "0";
    sortOper.setAttribute("bill-sorting-oper", "0");
    btnSortOper.forEach((item) => {
      item.classList.remove("active_sorting_oper");
    });
  }

  btnSortOper.forEach((item) => {
    item.addEventListener("click", () => {
      const setItem = item.getAttribute("data-sort-operation");
      const oldSortClient = sessionStorage.getItem("sortOper");
      if (oldSortClient == setItem) {
        sessionStorage.setItem("sortOper", "0");
        document.cookie = "sortOper= 0";
      } else {
        const operDate = item.getAttribute("data-sort-operation");
        sortOper.setAttribute("data-sort-operation", operDate);

        sessionStorage.setItem("sortOper", operDate);
        document.cookie = "sortOper=" + operDate;
      }

      location.reload();
    });

    const indexBtnOper = sortOper.getAttribute("bill-sorting-oper");
    const operDate = item.getAttribute("data-sort-operation");
    if (indexBtnOper == operDate) {
      item.classList.add("active_sorting_oper");
    }
  });
}
// установка сортировки месяца
const sortDate = document.querySelector(".bill-sorting-date");
if (sortDate) {
  const sortMonthReload = sessionStorage.getItem("sortMonth");
  if (sortMonthReload) {
    sortDate.setAttribute("bill-sorting-date", sortMonthReload);
  }else{
     sessionStorage.setItem("sortMonth", "1");
    sortDate.setAttribute("bill-sorting-date", "1");
  }

  const btnSort = document.querySelectorAll(".btn_sorting_month");

  btnSort.forEach((item) => {
    item.addEventListener("click", () => {
      const monthDate = item.getAttribute("data-sort-month");
      sortDate.setAttribute("data-sort-month", monthDate);
      sessionStorage.setItem("sortMonth", monthDate);
      document.cookie = "sortMonth=" + monthDate;
      location.reload();
    });

    const indexBtn = sortDate.getAttribute("bill-sorting-date");
    const monthDate = item.getAttribute("data-sort-month");
    if (indexBtn == monthDate) {
      item.classList.add("active_sorting");
    }
  });
}
