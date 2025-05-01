//новый месяц кнопка
const newBillMonth = document.querySelector(".new_month");
if (newBillMonth) {
  newBillMonth.addEventListener("click", () => {
    location.href = window.location.origin + "/service/new_month";
    window.history.back();
  });
}