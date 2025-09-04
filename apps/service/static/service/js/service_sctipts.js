//новый месяц кнопка
const newBillMonth = document.querySelector(".new_month");
if (newBillMonth) {
  newBillMonth.addEventListener("click", () => {
    location.href = window.location.origin + "/service/new_month";
    window.history.back();
  });
}


// вспомогательные функции для работы с куками (очистка на всех путях)
function deleteCookieOnAllPaths(name) {
  try {
    const pathSegments = location.pathname.split("/").filter(Boolean);
    let accumPath = "";
    // удаляем на всех вложенных путях, начиная с текущего и выше
    for (let i = 0; i <= pathSegments.length; i++) {
      const path = "/" + pathSegments.slice(0, i).join("/");
      document.cookie =
        name + "=;max-age=0;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=" + path + ";SameSite=Lax";
    }
  } catch (e) {
    // noop
  }
}

// // установка сортировки operation
const sortOper = document.querySelector(".bill-sorting-operation");
if (sortOper) {
  const sortOperReload = sessionStorage.getItem("sortOper");
  const btnSortOper = document.querySelectorAll(".btn_sorting_operation");

  if (sortOperReload) {
    sortOper.setAttribute("bill-sorting-oper", sortOperReload);
    // синхронизируем и чистим дубли без path
    deleteCookieOnAllPaths("sortOper");
    document.cookie = "sortOper=" + sortOperReload + ";path=/;max-age=2592000;SameSite=Lax";
  } else {
    deleteCookieOnAllPaths("sortOper");
    document.cookie = "sortOper=" + "0" + ";path=/;max-age=2592000;SameSite=Lax";
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
        deleteCookieOnAllPaths("sortOper");
        document.cookie = "sortOper=" + "0" + ";path=/;max-age=2592000;SameSite=Lax";
      } else {
        const operDate = item.getAttribute("data-sort-operation");
        sortOper.setAttribute("data-sort-operation", operDate);

        sessionStorage.setItem("sortOper", operDate);
        deleteCookieOnAllPaths("sortOper");
        document.cookie = "sortOper=" + operDate + ";path=/;max-age=2592000;SameSite=Lax";
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
    // синхронизируем куки с sessionStorage при загрузке страницы и чистим дубли
    deleteCookieOnAllPaths("sortMonth");
    document.cookie = "sortMonth=" + sortMonthReload + ";path=/;max-age=2592000;SameSite=Lax";
  }else{
     sessionStorage.setItem("sortMonth", "1");
    sortDate.setAttribute("bill-sorting-date", "1");
    // записываем дефолтное значение в куки, чтобы сервер видел его на всех путях, и чистим дубли
    deleteCookieOnAllPaths("sortMonth");
    document.cookie = "sortMonth=" + "1" + ";path=/;max-age=2592000;SameSite=Lax";
  }

  const btnSort = document.querySelectorAll(".btn_sorting_month");

  btnSort.forEach((item) => {
    item.addEventListener("click", () => {
      const monthDate = item.getAttribute("data-sort-month");
      sortDate.setAttribute("data-sort-month", monthDate);
      sessionStorage.setItem("sortMonth", monthDate);
      deleteCookieOnAllPaths("sortMonth");
      document.cookie = "sortMonth=" + monthDate + ";path=/;max-age=2592000;SameSite=Lax";
      location.reload();
    });

    const indexBtn = sortDate.getAttribute("bill-sorting-date");
    const monthDate = item.getAttribute("data-sort-month");
    if (indexBtn == monthDate) {
      item.classList.add("active_sorting");
    }
  });
}
