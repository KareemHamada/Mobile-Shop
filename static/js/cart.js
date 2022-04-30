var updateBtns = document.getElementsByClassName("update-cart")

for(i=0;i<updateBtns.length;i++){
    updateBtns[i].addEventListener("click", function() {

        action = this.dataset.action
        product_id = this.dataset.product

        if(user === "AnonymousUser"){
            console.log("Not logged in")
        }else{
            updateUserOrder(product_id,action)
        }
    });
}




function updateUserOrder(product_id,action){
    console.log("User is logged in")
    var url = "/updateItem/"
    fetch(url, {
    method: 'POST',  
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken' : csrftoken
    },
    body: JSON.stringify({"product_id" : product_id,"action":action}),
    })
    .then(response => response.json())
    .then(data => {
        console.log('data:', data);
        location.reload()
    })
    .catch((error) => {
    console.error('Error:', error);
    });

}



