// const modal_button = document.querySelectorAll(".open-modal");
const modal_add_client = document.querySelector(
    '[data-name="modal-add-client"]'
  );
  
  // const modal_windows = document.querySelector(".modal");
  
  // модалка первичного добавления клиента и контракта
  if (modal_add_client) {
    modal_add_client.addEventListener("click", () => {
      let elem = modal_add_client.getAttribute("data-name");
      const add_contract = document.querySelector(".client_contract_add");
      add_contract.disabled = true;
  
      modal(elem, add_contract);
      addManager();
      addmanagerContract();
      // очистка полей
      const contractWrapper = document.getElementById("modal_contract_wrapper");
      contractWrapper.innerHTML = "";
      const clientNameInput = document.querySelector(".modal-client_name");
      clientNameInput.innerHTML = "";
      clientNameInput.value = "";
  
      createInputContract();
      choiceColor();
      // валидация
      const modalWindows = document.getElementById(elem);
      modalWindows.addEventListener("input", () => {
        validate(elem, ".client_contract_add");
        validate(elem, ".modal_add_contract_btn");
      });
      // добавление изменение клиента контракта
      const endpointClient = "/api/v1/client/";
      const endpointContact = "/api/v1/contract/";
      const endpointContractAll = "/api/v1/contract/create_contracts/";
      const optionsMethod = "POST";
  
      addNewClient(
        elem,
        endpointClient,
        endpointContact,
        endpointContractAll,
        optionsMethod
      );
    });
  }
  
  // менеджеры из базы
  function addManager(selected, boss, divWrapper) {
    const endpoint = "/api/v1/employee/responsible_list/";
    let select;
    
  
    if (boss) {
      let select = document.createElement("select");
      if (selected > 0) {
        select.className = "modal-boss_client";
      } else {
        select.className = "modal-boss_client choice empty";
      }
  
      divWrapper.append(select);
  
      new selectOption(
        "modal-select empty",
        "0",
        "0",
        "Ответственный",
        "0",
        true
      ).appendTo(select);
  
      fetch(endpoint, {
        method: "get",
      })
        .then((response) => response.json())
        .then((data) => {
          const lengthData = data.length;
  
          data.forEach(function (value, index) {
            new selectOption(
              "modal-select",
              value.last_name,
              value.id,
              value.last_name,
              selected
            ).appendTo(select);
          });
         
          return;
        })
        .then(() => {
          return;
        });
    } else {
      // select = document.querySelector(".modal-manager_client");
      // if (selected > 0) {
      //   select.className = "";
      //   select.classList.add("modal-manager_client");
      // }
      // select.innerHTML = "";
      // new selectOption(
      //   "modal-select empty",
      //   "0",
      //   "0",
      //   "Менеджер",
      //   "0",
      //   true
      // ).appendTo(select);
      // fetch(endpoint, {
      //   method: "get",
      // })
      //   .then((response) => response.json())
      //   .then((data) => {
      //     i = 0;
      //     data.forEach(function (value, key) {
      //       i++;
      //       new selectOption(
      //         "modal-select",
      //         value.last_name,
      //         value.id,
      //         value.last_name,
      //         selected
      //       ).appendTo(select);
      //     });
      //     console.log(222);
      //     return;
      //   });
    }
  }
  
  function addmanagerContract(selected, boss, divWrapper) {
    console.log("addmanagerContract JS");
    const endpoint = "/api/v1/employee/manager_list/";
    let select;
    select = document.querySelector(".modal-manager_client");
    if (selected > 0) {
      select.className = "";
      select.classList.add("modal-manager_client");
    }
    select.innerHTML = "";
  
    new selectOption(
      "modal-select empty",
      "0",
      "0",
      "Менеджер",
      "0",
      true
    ).appendTo(select);
  
    fetch(endpoint, {
      method: "get",
    })
      .then((response) => response.json())
      .then((data) => {
        i = 0;
        data.forEach(function (value, key) {
          i++;
          new selectOption(
            "modal-select",
            value.last_name,
            value.id,
            value.last_name,
            selected
          ).appendTo(select);
        });
        preloaderModal((isLoading = false), (isLoaded = true));
        return;
      });
  }
  // сервисы из базы
  function addService(selectInput, selected, instans) {
    const select = selectInput;
    new selectOption("modal-select", "0", "", "Услуга").appendTo(select);
    const instance = "/api/v1/service/";
  
    fetch(instance, {
      method: "GET",
    })
      .then((response) => response.json())
      .then((data) => {
        data.forEach(function (value, key) {
          new selectOption(
            "modal-select input-130",
            value.id,
            value.id,
            value.name,
            selected
          ).appendTo(select);
        });
  
        return;
      });
  }
  
  // создание пустых строчек договоров
  function createInputContract() {
    const contractWrapper = document.getElementById("modal_contract_wrapper");
  
    let divWrapper = document.createElement("div");
    divWrapper.className = "modal_add_contract";
    contractWrapper.append(divWrapper);
  
    let select = document.createElement("select");
    select.className = "modal-service_type choice";
    divWrapper.append(select);
    addService(select);
    new Input(
      "text",
      "modal-client_contract-input input-200",
      "",
      "Номер договора"
    ).appendTo(divWrapper);
    new Input(
      "date",
      "modal-client_contract-input input-130 choice empty",
      "",
      "Подписан"
    ).appendTo(divWrapper);
    new Input(
      "text",
      "modal-client_contract-input input-130 pyb",
      "",
      "Сумма"
    ).appendTo(divWrapper);
    new Input("hidden", " 1", "0").appendTo(divWrapper);
  
    addManager("selected", "boss", divWrapper);
  
    let button = document.createElement("button");
    button.className = "modal_add_contract_btn";
    button.innerHTML = "OK";
    button.disabled = true;
    divWrapper.append(button);
  
    replaceNam();
    choiceColor();
  
    // preloaderModal((isLoading = false), (isLoaded = true));
    button.addEventListener("click", () => {
      button.remove();
      createInputContract();
    });
  }
  // отправка и обновление контракта клиента ПОСТ ЗАПРОСЫ
  function addNewClient(
    elem,
    endpointClient,
    endpointContact,
    endpointContractAll,
    optionsMethod,
    clientId
  ) {
    const add_contract = document.querySelector(".client_contract_add");
  
    add_contract.addEventListener("click", (event) => {
      let data = "";
      const clientName = document.querySelector(".modal-client_name").value;
      const manegeSelect = document.querySelector(".modal-manager_client");
      let managerProject =
        manegeSelect.options[manegeSelect.selectedIndex].getAttribute("data-id");
  
      let clientObj = {
        name: clientName,
        manager: +managerProject,
      };
      if (clientId != undefined) {
        clientObj["id"] = clientId;
      }
  
      data = JSON.stringify(clientObj);
  
      function getCookie(name) {
        let matches = document.cookie.match(
          new RegExp(
            "(?:^|; )" +
              name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, "\\$1") +
              "=([^;]*)"
          )
        );
        return matches ? decodeURIComponent(matches[1]) : undefined;
      }
      let csrfToken = getCookie("csrftoken");
  
      fetch(endpointClient, {
        method: optionsMethod,
        body: data,
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
      })
        .then((response) => response.json())
  
        .then((response) => {
          clientId = response.id;
          const contractArr = document.querySelectorAll(".modal_add_contract");
  
          let arrContractAll = [];
          let contractId;
          contractArr.forEach((element) => {
            let contractChild = element.childNodes;
  
            if (contractChild[1].value == "") {
              return;
            } else {
              let contractName = contractChild[1].value;
              const type_servise = contractChild[0];
              var servise =
                type_servise.options[type_servise.selectedIndex].getAttribute(
                  "data-id"
                );
              const data = contractChild[2].value;
              const contractSum = contractChild[3].value
                .replace(/[^+\d]/g, "")
                .replace(/(\d)\++/g, "$1");
  
              const bossContractInp = contractChild[5];
              var bossContr =
                bossContractInp.options[
                  bossContractInp.selectedIndex
                ].getAttribute("data-id");
  
              const contractObj = {
                client: clientId,
                contract_number: contractName,
                date_start: data,
                service: servise,
                // manager: managerProject,
                contract_sum: contractSum,
                manager: bossContr,
              };
  
              if (contractChild[4].value != "0") {
                contractId = contractChild[4].value;
                contractObj["id"] = contractId;
              } else {
                contractId = "";
                contractObj["id"] = contractId;
              }
  
              arrContractAll.push(contractObj);
            }
          });
          let endpointTwo;
  
          let data;
          if (arrContractAll.length > 1) {
            endpointTwo = endpointContractAll;
            data = JSON.stringify(arrContractAll);
          } else {
            if (contractId) {
              endpointTwo = endpointContact + contractId + "/";
            } else {
              endpointTwo = endpointContact;
              optionsMethod = "POST";
            }
  
            objContractAll = arrContractAll[0];
            data = JSON.stringify(objContractAll);
          }
          console.log()
          fetch(endpointTwo, {
            method: optionsMethod,
            body: data,
            headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": csrfToken,
            },
          }).then((response) => {
         
            if (response.ok) {
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
    });
  }
  // модалка обновления клиента контракта
  const updInfo = document.querySelectorAll(".upd_info");
  updInfo.forEach((element) => {
    element.addEventListener("click", () => {
      preloaderModal((isLoading = true), (isLoaded = false));
      // const modalWindows = document.querySelector(".modal");
      let elem = element.getAttribute("data-name");
      let clientName = element.getAttribute("data-client-name");
  
      modal(elem);
      const contractWrapper = document.getElementById("modal_contract_wrapper");
      contractWrapper.innerHTML = "";
  
      updClientContract(element, clientName, elem);
  
      // валидация
      const modalWindows = document.getElementById(elem);
      // modalWindows.addEventListener("input", () => {
      //   validate(elem, ".client_contract_add");
      // });
      // const wrapLAst = document.getElementById("modal_contract_wrapper").childNodes
      // const lastCount = wrapLAst.length
  
      modalWindows.addEventListener("input", () => {
        validateBtn(elem, ".modal_add_contract_btn");
      });
      const idClient = element.getAttribute("data-client-id");
  
      const endpointClient = "/api/v1/client/" + idClient + "/";
      const endpointContact = "/api/v1/contract/";
      //  + contractId + "/"
      const endpointContractAll = "/api/v1/contract/upd_contracts/";
      const optionsMethod = "PUT";
  
      addNewClient(
        elem,
        endpointClient,
        endpointContact,
        endpointContractAll,
        optionsMethod,
        idClient
      );
    });
  });
  
  //забрать имя клиента
  function updClientContract(element, clientName, elem) {
    const titleModal = document.querySelector(".modal-client_title");
    titleModal.innerHTML = "изменить клиента";
    const idClient = element.getAttribute("data-client-id");
    getContracts(idClient, elem);
  
    const clientNameInput = document.querySelector(".modal-client_name");
    clientNameInput.value = clientName;
  }
  
  //получить контракты по имени клиента
  function getContracts(idClient, elem) {
    //  preloaderModal(isLoading = true,isLoaded = false);
  
    // сами контраты получение
    const endpoint = "/api/v1/contract/" + idClient + "/contract_li/";
    fetch(endpoint, {
      method: "get",
    })
      .then((response) => response.json())
      .then((data) => {
        const contractWrapper = document.getElementById("modal_contract_wrapper");
        i = 0;
        data.forEach((el) => {
          // // запись менеджера
          // manager = el.manager;
          // addManager(manager);
  
          let divWrapper = document.createElement("div");
          divWrapper.className = "modal_add_contract";
          contractWrapper.append(divWrapper);
  
          //запись услуг
          let select = document.createElement("select");
          select.className = "modal-service_type";
          divWrapper.append(select);
          addService(select, el.service);
  
          new Input(
            "text",
            "modal-client_contract-input input-200",
            el.contract_number,
            "Номер договора"
          ).appendTo(divWrapper);
  
          new Input(
            "date",
            "modal-client_contract-input input-130 choice empty",
            el.date_start,
            "Подписан"
          ).appendTo(divWrapper);
  
          new Input(
            "text",
            "modal-client_contract-input input-130 pyb",
            el.contract_sum,
            "Сумма"
          ).appendTo(divWrapper);
          new Input("hidden", " ", el.id, "").appendTo(divWrapper);
  
          // let selectBoss = document.createElement("select");
          // selectBoss.className = "modal-boss_client";
          // divWrapper.append(selectBoss);
          manager = el.manager;
          addManager(manager, "boss", divWrapper);
  
          replaceNam();
        });
        createInputContract();
      })
      .then((data) => {
        
        fetch("/api/v1/client/" + idClient + "/manager_li/", {
          method: "get",
        })
          .then((response) => response.json())
          .then((data) => {
            data.forEach((el) => {
              // запись менеджера
              manager = el.manager;
              addmanagerContract(manager);
            });
          });
      });
  
    //   fetch("/clients/api/client/" + idClient + "/manager_li/", {
    //     method: "get",
    //   })
    //     .then((response) => response.json())
    //     .then((data) => {
    //       data.forEach((el) => {
    //         // запись менеджера
    //         manager = el.manager;
    //         addmanagerContract(manager);
    //       });
    //     });
  }
  
  //сортировка по категориям
  sortingClient();
  function sortingClient() {
    const btnClientSort = document.querySelectorAll(".btn_client_sort");
    const sortClient = sessionStorage.getItem("sortClient");
  
    btnClientSort.forEach((elem) => {
      if (sortClient == elem.getAttribute("data-sort-client")) {
        elem.style.borderColor = "#000";
      }
      elem.addEventListener("click", () => {
        const setItem = elem.getAttribute("data-sort-client");
        const oldSortClient = sessionStorage.getItem("sortClient");
        if (oldSortClient == setItem) {
          sessionStorage.removeItem("sortClient");
          document.cookie = "sortClient= client";
        } else {
          const sortClient = sessionStorage.setItem("sortClient", setItem);
          document.cookie = "sortClient=" + setItem;
        }
        location.reload();
      });
    });
  }
  