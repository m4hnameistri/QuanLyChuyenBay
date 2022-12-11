// function pay() {
//     if (confirm("Bạn chắc chắn thanh toán không?") == true) {
//         fetch("/api/pay").then(res => res.json()).then(data => {
//             if (data.status === 200)
//                 location.reload()
//         })
//     }

// }

function SelectedTicketClass() {
    var btn = document.querySelector('#pay');        
    var radioButtons = document.querySelectorAll('input[name="ticket_class"]');
    // btn.addEventListener("click", () => {
        for (var i = 0; i < radioButtons.length; i++) {
            if (radioButtons[i].checked) {
                var selectedClass = radioButtons[i].value;
                var selectedPrice = $(radioButtons[i]).attr("data-price");
                return [selectedClass,selectedPrice];
            }
        }        
// });
}

function payment(flight_id, ticket_class_id, ticket_price_id){
    if (confirm("Bạn chắc chắn thanh toán không?") == true){
        fetch("/api/payment", {
            method: "post",
            body: JSON.stringify({
                "flight_id": flight_id,
                "ticket_class_id": ticket_class_id,
                "ticket_price_id": ticket_price_id,
            }),
            headers: {
                "Content-Type": "application/json"
            }
        }).then((res) => res.json()).then((data) => {
            if (data.status === 200)
                location.reload()
        }) // js promise
    }   
}