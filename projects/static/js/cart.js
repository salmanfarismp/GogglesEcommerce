var updateBtns = document.getElementsByClassName('update-cart')

for (var i=0; i<updateBtns.length;i++){
    updateBtns[i].addEventListener('click', function(){
        var productId = this.dataset.product
        var action = this.dataset.action
        console.log('product:',productId,action)
        console.log('User:',user)

        if (user === 'AnonymousUser'){
            console.log('Not Logged In')
        }else{
            updateUserOrder(productId,action);
        }
    })
}
function updateUserOrder(productId,action){
    console.log('User is logged in sending data..')

    var url = '/update_item'
    fetch(url ,{
        method :'POST',
        headers:{
            'Content-Type':'application/json',
            'X-CSRFToken':csrftoken,
        },
        body:JSON.stringify({'productid': productId,'action':action})

        
    })

    .then((response) =>{
        return response.json()
    })
    .then((data) =>{
        location.reload()
        return console.log('data:', data)
        
    })

}