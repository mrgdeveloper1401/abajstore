const productName = document.querySelectorAll(".productName");
const navBarLinks = document.querySelector("#navBarLinks");
const hiddenContent = document.querySelector("#hiddenContent");
const hiddenScrollDiv = document.querySelector("#hiddenScrollDiv");
const sortsProductsLinkCont = document.querySelectorAll(
  "#sortsProductsLinkCont a"
);
const producsUl = document.querySelectorAll("#producsUlParent ul");
const accountSetting = document.querySelector("#accountSetting");
const accountSettingCont = document.querySelector("#accountSettingCont");
const mainMenuNavBarClickElement = document.querySelectorAll(
  ".mainMenuNavBarClickElement"
);
const mainMenuNavBarClickElementUls = document.querySelectorAll(
  ".mainMenuNavBarClickElement + ul"
);
const closeMainMenuNavBar = document.querySelector("#closeMainMenuNavBar");
const mainMenuNavBarsec = document.querySelector("#mainMenuNavBarsec");
const openMainMenuNavBar = document.querySelector("#openMainMenuNavBar");
const scrollTop = document.querySelector("#scrollTop");

const header = document.querySelector("header");
const main = document.querySelector("main");
if (document.body.children[0] === header) {
  header.classList.add("lg:fixed");
  if (innerWidth > 1023)
    main.style.paddingTop = header.scrollHeight + 20 + "px";
  else main.style.paddingTop = "";
} else {
  header.classList.remove("lg:fixed");
  main.style.paddingTop = "0px";
  main.className = "";
  header.style.zIndex = "100";
  header.style.position = "relative";
}
let oldScrollY = scrollY;
let istouch = true;
productName.forEach((input) => {
  input.addEventListener("focus", () => {
    hiddenContent.classList.add("show");
    input.parentElement.classList.add("headerFormFoucsStyle");
    input.id = "search";
    location.hash = input.id;
  });
  input.addEventListener("blur", () => {
    hiddenContent.classList.remove("show");
    input.parentElement.classList.remove("headerFormFoucsStyle");
    input.id = "";
    location.hash = "";
  });
});

navBarLinks.addEventListener("mouseover", () => {
  productName.forEach((input) => {
    input.blur();
  });
  hiddenContent.classList.add("show");
});
navBarLinks.addEventListener("mouseleave", () => {
  hiddenContent.classList.remove("show");
});

window.addEventListener("scroll", () => {
  if (oldScrollY > scrollY) {
    oldScrollY = scrollY;
    hiddenScrollDiv.parentElement.classList.remove("hideWithTranslateY");
  } else if (oldScrollY <= scrollY) {
    oldScrollY = scrollY;
    hiddenScrollDiv.parentElement.classList.add("hideWithTranslateY");
  }
  if (innerWidth > 1023 && document.body.children[0] !== header) {
    if (header.offsetTop < scrollY) {
      header.style.position = "fixed";
      main.classList.add("lg:pt-[140px]");
    } else {
      main.style.paddingTop = "0px";
      main.className = "";
      header.style.position = "relative";
      header.style.zIndex = "100";
    }
  } else if (document.body.children[0] === header) {
    header.classList.add("lg:fixed");
    main.classList.add("lg:pt-[140px]");
    header.style.position = "";
  } else if (innerWidth < 1023) {
    header.style.position = "relative";
    header.style.zIndex = "100";
  }
});
window.addEventListener("resize", () => {
  let padTop = 0;
  if (document.body.children[0] === header) {
    padTop = header.scrollHeight + 20;
  } else {
    padTop = document.body.children[0].scrollHeight + header.scrollHeight + 20;
  }
  if (innerWidth < 1023) {
    main.style.paddingTop = "";
  } else {
    main.style.paddingTop = padTop;
  }
  if (header.style.position === "relative") {
    main.style.paddingTop = "0px";
    main.className = "";
  }
});
Array.from(sortsProductsLinkCont).forEach((link, index) => {
  link.addEventListener("mouseover", () => {
    Array.from(sortsProductsLinkCont).forEach((item, ind) => {
      producsUl[ind].classList.remove("flexShow");
      item.classList.remove("headerNavHoverStyle");
    });
    link.classList.add("headerNavHoverStyle");
    producsUl.forEach((ul) => {
      if (link.value === producsUl[index].value)
        producsUl[index].classList.add("flexShow");
    });
  });
});
window.addEventListener("click", (e) => {
  if (!accountSetting) return;
  if (
    e.target !== accountSetting &&
    e.target !== accountSetting.children[0] &&
    e.target !== accountSetting.children[1]
  ) {
    if (accountSettingCont) accountSettingCont.classList.remove("show");
  }
});
if (accountSetting)
  accountSetting.addEventListener("click", () => {
    accountSettingCont.classList.toggle("show");

    istouch = true;
  });
mainMenuNavBarClickElement.forEach((btn, index) => {
  btn.addEventListener("click", () => {
    mainMenuNavBarClickElementUls[index].classList.toggle("showUl");
    btn.classList.toggle("showed");
  });
});

openMainMenuNavBar.addEventListener("click", () => {
  mainMenuNavBarsec.classList.remove("hidden");
  mainMenuNavBarsec.classList.add("setDisplay");
  mainMenuNavBarsec.classList.add("active");
});

mainMenuNavBarsec.addEventListener("click", (e) => {
  console.log(e.target);
  if (e.target !== mainMenuNavBarsec && e.target !== openMainMenuNavBar) return;
  mainMenuNavBarsec.classList.remove("active");
});

mainMenuNavBarsec.onanimationend = () => {
  if (!mainMenuNavBarsec.classList.contains("active"))
    mainMenuNavBarsec.classList.remove("setDisplay");
};

closeMainMenuNavBar.addEventListener("click", () => mainMenuNavBarsec.click());
scrollTop.addEventListener("click", () => {
  scrollTo(0, 0);
});

window.addEventListener("scroll", () => {
  if (scrollY > 100) scrollTop.classList.add("active");
  else scrollTop.classList.remove("active");
});

(function () {
  const setFormatNumber = document.querySelectorAll(".setFormatNumber");
  setFormatNumber.forEach((item) => {
    if (item.value)
      item.value = Number(item.value.replace(/\,/g, "")).toLocaleString();
    else
      item.textContent = Number(
        item.textContent.replace(/\,/g, "")
      ).toLocaleString();
  });
})();
