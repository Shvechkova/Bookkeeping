const addEmployee = document.querySelectorAll(
  '[data-name="modal-btn_add_employee"]'
);

if (addEmployee) {
  addEmployee.forEach((element) => {
    element.addEventListener("click", (event) => {
      const battonAdd = document.querySelector(".btn_add_employee_batton");
      let elem = element.getAttribute("data-name");
      let step = element.getAttribute("data-step");

      modal(elem, battonAdd);
      // валидация
      const modalWindows = document.getElementById(elem);
      
      const employeeTitle = document.querySelector(
        ".modal_title_employee_text"
      );

      const dataStop = modalWindows.querySelector(".input_box_stop");
      if (step == "1") {
        dataStop.style.display = "none";
   
        employeeTitle.innerHTML = "Добавить сотрудника";
        AddEmployeeFetch(element, elem, modalWindows, battonAdd);
        const dateStopInput =  modalWindows.querySelector("#data_employee_stop")
        dateStopInput.valueAsDate =
        new Date();
        const modalLastName = modalWindows.querySelector(
          ".modal_add_employee_input_last_name"
        );
        const modalName = modalWindows.querySelector(
          ".modal_add_employee_input_name"
        );
        const modalDateStart = modalWindows.querySelector(
          "#data_employee_start"
        );
       

        modalLastName.value = "";
        modalName.value = "";
        modalDateStart.value = "";
        modalWindows.addEventListener("input", () => {
          validate(elem, ".btn_add_employee_batton ");
        });
       
      } else if (step == "2") {
        dataStop.style.display = "block";
        employeeTitle.innerHTML = "Изменить сотрудника";
        addInfoEmployeeFetch(element, elem, modalWindows,battonAdd)
        battonAdd.disabled = false;
      }
    });
  });
}

function AddEmployeeFetch(element, elem, modalWindows, battonAdd) {
  battonAdd.addEventListener("click", () => {
    const name = modalWindows.querySelector(
      ".modal_add_employee_input_name"
    ).value;
    const lastName = modalWindows.querySelector(
      ".modal_add_employee_input_last_name"
    ).value;
    const dataStart = modalWindows.querySelector(
      ".modal_add_employee_input_date"
    ).value;
    console.log(dataStart);
    const form = new FormData();
    form.append("name", name);
    form.append("last_name", lastName);
    form.append("type", "EXTERNAL");
    form.append("date_start", dataStart);

    let object = {};
    form.forEach((value, key) => (object[key] = value));
    const dataJson = JSON.stringify(object);

    let csrfToken = getCookie("csrftoken");
    endpoint = "/employee/api/employees/";
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
        }, 400);
      } else {
        const windowContent = document.getElementById(elem);

        alertError(windowContent);
        const timerId = setTimeout(() => {
          location.reload();
        }, 400);
      }
    });
  });
}

function addChangeEmployee() {}
function addInfoEmployeeFetch(element, elem, modalWindows,battonAdd) {
  const employeeId = element.getAttribute("data-employee-id");
  const employeeName = element.getAttribute("data-employee-name");
  const employeeLastName = element.getAttribute("data-employee-last-name");
  const employeeDateStart = element.getAttribute("data-employee-data-start");
  const employeeDateEnd = element.getAttribute("data-employee-data-end");

  const modalLastName = modalWindows.querySelector(
    ".modal_add_employee_input_last_name"
  );
  const modalName = modalWindows.querySelector(
    ".modal_add_employee_input_name"
  );
  const modalDateStart = modalWindows.querySelector("#data_employee_start");
  const modalDateEnd = modalWindows.querySelector("#data_employee_stop");

  modalLastName.value = employeeLastName;
  modalName.value = employeeName;
  modalDateStart.value = employeeDateStart;
  modalDateStart.classList.remove("empty")
  modalDateEnd.value = employeeDateEnd
  if (employeeDateEnd != ""){
    modalDateEnd.classList.remove("empty")
  }

  battonAdd.addEventListener("click", () => {
    const name = modalWindows.querySelector(
      ".modal_add_employee_input_name"
    ).value;
    const lastName = modalWindows.querySelector(
      ".modal_add_employee_input_last_name"
    ).value;
    const dataStart = modalWindows.querySelector(
      ".modal_add_employee_input_date"
    ).value;
    const dataEnd = modalWindows.querySelector(
      ".modal_add_employee_input_date_stop"
    ).value;

    const form = new FormData();
    form.append("name", name);
    form.append("last_name", lastName);
    form.append("type", "EXTERNAL");
    form.append("date_start", dataStart);

    if (dataEnd != ""){
      form.append("date_end", dataEnd)
    }

    let object = {};
    form.forEach((value, key) => (object[key] = value));
    const dataJson = JSON.stringify(object);

    const endpoint = "/employee/api/employees/" + employeeId + "/";

    let csrfToken = getCookie("csrftoken");

    fetch(endpoint, {
      method: "PUT",
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
        }, 400);
      } else {
        const windowContent = document.getElementById(elem);

        alertError(windowContent);
        const timerId = setTimeout(() => {
          location.reload();
        }, 400);
      }
    });
  })
}
