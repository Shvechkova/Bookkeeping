const shrinkItemOperAccount = document.querySelectorAll(
  ".btn_year_oper_accounr-shrink"
);
if (shrinkItemOperAccount) {
  shrinkItemOperAccount.forEach((element, i) => {
    let shrink = [];
    let shrinkElemToDate = {};
    element.addEventListener("click", () => {
      const itemShrinkName = element.getAttribute("data-created-btn");
      const itemShrink = document.querySelectorAll(
        `[data-created='${itemShrinkName}']`
      );
      const dataShrinkType = element.getAttribute("data-btn-type-shrink");

      const dateShrinkElem = {};

      itemShrink.forEach((elem) => {
        const dataCreatedShrink = elem.getAttribute("data-created");
        const dataShrink = elem.getAttribute("data-shrink");
        const dataShrinkItemType = elem.getAttribute("data-type-shrink");

        if (
          dataShrinkType == dataShrinkItemType &&
          dataCreatedShrink == itemShrinkName
        ) {
          if (dataShrink === "none") {
            elem.setAttribute("data-shrink", "block");
            element.setAttribute("data-btn-deg", "0");
            element.setAttribute(`data-btn-deg-${dataShrinkItemType}`, "0");
            let btndeg = "data-btn-deg-" + dataShrinkItemType;

            shrinkElemToDate = {
              date: dataCreatedShrink,
              type: dataShrinkItemType,
              "data-shrink": "block",
              btndeg: 0,
            };
          } else {
            elem.setAttribute("data-shrink", "none");
            element.setAttribute(`data-btn-deg-${dataShrinkItemType}`, "180");

            let btndeg = "data-btn-deg-" + dataShrinkItemType;

            shrinkElemToDate = {
              date: dataCreatedShrink,
              type: dataShrinkItemType,
              datashrink: "none",
              btndeg: 180,
            };
          }
        }
      });

      var oldSheink = localStorage.getItem("shrinks");
      const oldSheinkPars = JSON.parse(oldSheink);

      if (oldSheink) {
        const lenghtold = Object.keys(oldSheinkPars).length;
        e = 0;
        oldSheinkPars.forEach((elem, i) => {
          e++;
          if (
            elem.date == shrinkElemToDate.date &&
            elem.type == shrinkElemToDate.type
          ) {
            oldSheinkPars[i] = shrinkElemToDate;
          } else {
            if (e === lenghtold) {
              oldSheinkPars.push(shrinkElemToDate);
            }
          }
        });

        localStorage.setItem("shrinks", JSON.stringify(oldSheinkPars));
      } else {
        shrink.push(shrinkElemToDate);
        localStorage.setItem("shrinks", JSON.stringify(shrink));
      }
    });
  });
}

//сортировка по категориям
sortingClient();
function sortingClient() {
  const btnClientSort = document.querySelectorAll(".oper_account_sort_bank");
  const sortClient = sessionStorage.getItem("sortOperAccount");

  btnClientSort.forEach((elem) => {
    if (sortClient == elem.getAttribute("data-sort-operation")) {
      elem.style.borderColor = "#000";
      elem.classList.add("oper_account_sort_bank-active");
    }
    elem.addEventListener("click", () => {
      const setItem = elem.getAttribute("data-sort-operation");
      const oldSortClient = sessionStorage.getItem("sortOperAccount");
      if (oldSortClient == setItem) {
        sessionStorage.removeItem("sortOperAccount");
        document.cookie = "sortOperAccount= 0";
      } else {
        const sortClient = sessionStorage.setItem("sortOperAccount", setItem);
        document.cookie = "sortOperAccount=" + setItem;
      }
      location.reload();
    });
  });
}
