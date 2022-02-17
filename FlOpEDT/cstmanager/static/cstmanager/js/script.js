outputSlider = (id, val) => {
    val = val == 8 ? 0 : val;
    let ele = document.getElementById(id);
    ele.innerHTML = val;
}
console.log("ok")