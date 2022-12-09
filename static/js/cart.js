function pay() {
    if (confirm("Bạn chắc chắn thanh toán không?") == true) {
        fetch("/api/pay").then(res => res.json()).then(data => {
            if (data.status === 200)
                window.location = url_for('index')
        })
    }

}