function setDataAsSaved() {
    $(".data-modified")
        .removeClass("data-modified")
        .addClass("data-saved");
}

function setDataAsError() {
    $(".data-modified")
        .removeClass("data-modified")
        .addClass("data-error");
}

function setRowsAsModified(td) {
    td.parent("tr")
        .removeClass("data-error")
        .removeClass("data-saved")
        .addClass("data-modified");
}

function postForm(form, url) {
    const options = {
        method: "POST",
        url: url,
        data: form.serialize(),
        headers: {
            "Accept": "application/json; charset=utf-8",
        },
    };

    $.ajax(options)
        .done(json => json && json.success ? setDataAsSaved() : setDataAsError())
        .fail(setDataAsError);
}

function onInputChange(ev) {
    const input = $(ev.currentTarget);
    const quantity = parseFloat(input.val());
    const td = $(ev.currentTarget).parent("[data-quantity]");
    const id = td.attr("data-quantity");
    const priceString = $(`[data-price='${id}']`).text();
    const price = parseFloat(priceString.replace(".", "").replace(",", "."));
    const subtotal = quantity && price ? (quantity * price).toFixed(2) : "";

    setRowsAsModified(td);
    $(`[data-subtotal='${id}']`).text(subtotal);
    postForm($("#comanda"), window.location.href);
}

function boxesReportUpdates() {
    $("[data-quantity] input").change(onInputChange);
}
