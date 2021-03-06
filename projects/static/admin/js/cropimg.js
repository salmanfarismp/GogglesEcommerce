const imagebox = document.getElementById('image-box')
    // crop-btn is the id of button that will trigger the event of change original file with cropped file.
    const crop_btn = document.getElementById('crop-btn')
    // id_image is the id of the input tag where we will upload the image
    const input = document.getElementById('id_product_image')
    var allowedExtensions =
        /(\.jpg|\.jpeg|\.png|\.gif)$/i;

    var filePath = input.value;

    // When user uploads the image this event will get triggered
    input.addEventListener('change', () => {
        if (!allowedExtensions.exec(input.value)) {
            alert('Invalid file type');
            input.value = '';
        }
        else {
            // Getting image file object from the input variable
            const img_data = input.files[0]
            // createObjectURL() static method creates a DOMString containing a URL representing the object given in the parameter.
            // The new object URL represents the specified File object or Blob object.
            const url = URL.createObjectURL(img_data)

            // Creating a image tag inside imagebox which will hold the cropping view image(uploaded file) to it using the url created before.
            imagebox.innerHTML = `<img src="${url}" id="image" style="width:100%;">`

            // Storing that cropping view image in a variable
            const image = document.getElementById('image')

            // Displaying the image box
            document.getElementById('image-box').style.display = 'block'
            // Displaying the Crop buttton
            document.getElementById('crop-btn').style.display = 'block'
            // Hiding the Post button
            document.getElementById('confirm-btn').style.display = 'none'

            // Creating a croper object with the cropping view image
            // The new Cropper() method will do all the magic and diplay the cropping view and adding cropping functionality on the website
            // For more settings, check out their official documentation at https://github.com/fengyuanchen/cropperjs
            const cropper = new Cropper(image, {
                autoCropArea: 1,
                viewMode: 1,
                scalable: false,
                zoomable: false,
                movable: false,
                aspectRatio: 1 / 1,
                //  preview: '.preview',
                minCropBoxWidth: 200,
                minCropBoxHeight: 200,
            })

            // When crop button is clicked this event will get triggered
            crop_btn.addEventListener('click', () => {
                // This method coverts the selected cropped image on the cropper canvas into a blob object
                cropper.getCroppedCanvas().toBlob((blob) => {

                    // Gets the original image data
                    let fileInputElement = document.getElementById('id_product_image');
                    // Make a new cropped image file using that blob object, image_data.name will make the new file name same as original image
                    let file = new File([blob], img_data.name, { type: "image/*", lastModified: new Date().getTime() });
                    // Create a new container
                    let container = new DataTransfer();
                    // Add the cropped image file to the container
                    container.items.add(file);
                    // Replace the original image file with the new cropped image file
                    fileInputElement.files = container.files;
                    console.log(container.files[0])
                    let img = container.files[0]
                    const url = URL.createObjectURL(img)
                    document.getElementById('image1').src = url




                    // Hide the cropper box
                    document.getElementById('image-box').style.display = 'none'
                    // Hide the crop button
                    document.getElementById('crop-btn').style.display = 'none'
                    // Display the Post button
                    document.getElementById('confirm-btn').style.display = 'block'

                });
            });
        }
    });


    //image2

    const input2 = document.getElementById('id_product_img_left')
    var allowedExtensions =
        /(\.jpg|\.jpeg|\.png|\.gif)$/i;

    var filePath = input2.value;

    // When user uploads the image this event will get triggered
    input2.addEventListener('change', () => {
        if (!allowedExtensions.exec(input2.value)) {
            alert('Invalid file type');
            input2.value = '';
        }
        else {
            // Getting image file object from the input variable
            const img_data = input2.files[0]
            // createObjectURL() static method creates a DOMString containing a URL representing the object given in the parameter.
            // The new object URL represents the specified File object or Blob object.
            const url = URL.createObjectURL(img_data)

            // Creating a image tag inside imagebox which will hold the cropping view image(uploaded file) to it using the url created before.
            imagebox.innerHTML = `<img src="${url}" id="image02" style="width:100%;">`

            // Storing that cropping view image in a variable
            const image = document.getElementById('image02')
            console.log(image)
            // Displaying the image box
            document.getElementById('image-box').style.display = 'block'
            // Displaying the Crop buttton
            document.getElementById('crop-btn').style.display = 'block'
            // Hiding the Post button
            document.getElementById('confirm-btn').style.display = 'none'

            // Creating a croper object with the cropping view image
            // The new Cropper() method will do all the magic and diplay the cropping view and adding cropping functionality on the website
            // For more settings, check out their official documentation at https://github.com/fengyuanchen/cropperjs
            const cropper = new Cropper(image, {
                autoCropArea: 1,
                viewMode: 1,
                scalable: false,
                zoomable: false,
                movable: false,
                aspectRatio: 1 / 1,
                //  preview: '.preview',
                minCropBoxWidth: 200,
                minCropBoxHeight: 200,
            })

            // When crop button is clicked this event will get triggered
            crop_btn.addEventListener('click', () => {
                // This method coverts the selected cropped image on the cropper canvas into a blob object
                cropper.getCroppedCanvas().toBlob((blob) => {

                    // Gets the original image data
                    let fileInputElement = document.getElementById('id_product_img_left');
                    // Make a new cropped image file using that blob object, image_data.name will make the new file name same as original image
                    let file = new File([blob], img_data.name, { type: "image/*", lastModified: new Date().getTime() });
                    // Create a new container
                    let container = new DataTransfer();
                    // Add the cropped image file to the container
                    container.items.add(file);
                    // Replace the original image file with the new cropped image file
                    fileInputElement.files = container.files;
                    console.log(container.files[0])
                    let img = container.files[0]
                    const url = URL.createObjectURL(img)
                    document.getElementById('image2').src = url




                    // Hide the cropper box
                    document.getElementById('image-box').style.display = 'none'
                    // Hide the crop button
                    document.getElementById('crop-btn').style.display = 'none'
                    // Display the Post button
                    document.getElementById('confirm-btn').style.display = 'block'

                });
            });
        }
    });



  //image-3
    const input3 = document.getElementById('id_product_img_right')
    var allowedExtensions =
        /(\.jpg|\.jpeg|\.png|\.gif)$/i;

    var filePath = input3.value;

    // When user uploads the image this event will get triggered
    input3.addEventListener('change', () => {
        if (!allowedExtensions.exec(input3.value)) {
            alert('Invalid file type');
            input3.value = '';
        }
        else {
            // Getting image file object from the input variable
            const img_data = input3.files[0]
            // createObjectURL() static method creates a DOMString containing a URL representing the object given in the parameter.
            // The new object URL represents the specified File object or Blob object.
            const url = URL.createObjectURL(img_data)

            // Creating a image tag inside imagebox which will hold the cropping view image(uploaded file) to it using the url created before.
            imagebox.innerHTML = `<img src="${url}" id="image03" style="width:100%;">`

            // Storing that cropping view image in a variable
            const image = document.getElementById('image03')

            // Displaying the image box
            document.getElementById('image-box').style.display = 'block'
            // Displaying the Crop buttton
            document.getElementById('crop-btn').style.display = 'block'
            // Hiding the Post button
            document.getElementById('confirm-btn').style.display = 'none'

            // Creating a croper object with the cropping view image
            // The new Cropper() method will do all the magic and diplay the cropping view and adding cropping functionality on the website
            // For more settings, check out their official documentation at https://github.com/fengyuanchen/cropperjs
            const cropper = new Cropper(image, {
                autoCropArea: 1,
                viewMode: 1,
                scalable: false,
                zoomable: false,
                movable: false,
                aspectRatio: 1 / 1,
                //  preview: '.preview',
                minCropBoxWidth: 200,
                minCropBoxHeight: 200,
            })

            // When crop button is clicked this event will get triggered
            crop_btn.addEventListener('click', () => {
                // This method coverts the selected cropped image on the cropper canvas into a blob object
                cropper.getCroppedCanvas().toBlob((blob) => {

                    // Gets the original image data
                    let fileInputElement = document.getElementById('id_product_img_right');
                    // Make a new cropped image file using that blob object, image_data.name will make the new file name same as original image
                    let file = new File([blob], img_data.name, { type: "image/*", lastModified: new Date().getTime() });
                    // Create a new container
                    let container = new DataTransfer();
                    // Add the cropped image file to the container
                    container.items.add(file);
                    // Replace the original image file with the new cropped image file
                    fileInputElement.files = container.files;
                    console.log(container.files[0])
                    let img = container.files[0]
                    const url = URL.createObjectURL(img)
                    document.getElementById('image3').src = url

                    // Hide the cropper box
                    document.getElementById('image-box').style.display = 'none'
                    // Hide the crop button
                    document.getElementById('crop-btn').style.display = 'none'
                    // Display the Post button
                    document.getElementById('confirm-btn').style.display = 'block'

                });
            });
        }
    });


