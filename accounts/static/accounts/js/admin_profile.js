$(document).ready(function () {
    $('#selectedPhotos').on('click', '.remove-photo', function () {
        var index = $(this).data('index');
        var requestData = {
            photoId: parseInt(index),
            csrfmiddlewaretoken: csrf_token
        };
        $.ajax({
            url: '/ajax/accounts/profile/purchase_photo/delete',
            method: 'POST',
            data: requestData,

        }).then(
            $(this).parent().remove()
        );
    });
    $('#photos').change(function (event) {
        var files = event.target.files;
        var data = new FormData();

        var purchaseId = $('#photo_form_id').val();

        for (var i = 0; i < files.length; i++) {
            data.append("file", files[i]);
        }

        // Добавляем CSRF-токен в данные
        data.append("purchaseId", purchaseId)
        data.append('csrfmiddlewaretoken', csrf_token);

        $.ajax({
            url: '/ajax/accounts/profile/purchase_photo/add',           // адрес серверного обработчика
            type: 'POST',
            data: data,
            cache: false,
            processData: false,
            contentType: false
        }).done(function (response) {
            if (response.status) {
                $('#photo_form_id').val(purchaseId);
                $('#photoModal').modal('show');

                // Очищаем предыдущие превью фотографий
                $('#selectedPhotos').addClass("row row-cols-1 row-cols-md-3 g-4").empty();

                var photos = response.photos;

                for (var i = 0; i < photos.length; i++) {
                    var photoDiv = $('<div>')
                        .addClass('col')
                        .appendTo('#selectedPhotos');

                    var cardDiv = $('<div>')
                        .addClass('card')
                        .appendTo(photoDiv);

                    var imgElement = $('<img>')
                        .addClass('card-img-top mr-2 mb-2')
                        .attr('src', photos[i].url)
                        .attr('height', '250')
                        .appendTo(cardDiv);

                    var removeButton = $('<button>')
                        .addClass('col-6 d-grid mx-auto content-md-center btn btn-outline-danger btn-sm remove-photo')
                        .text('Remove')
                        .attr('data-index', photos[i].id)
                        .appendTo(cardDiv);

                    imgElement.after(removeButton);
                }
            }
        });
    })
});

function getPurchaseData(purchaseId) {
    var requestData = {
        purchaseId: parseInt(purchaseId),
        csrfmiddlewaretoken: csrf_token
    };

    $.ajax({
        data: requestData,
        method: 'POST',
        url: '/ajax/accounts/profile/purchase_photo/get',
    }).then((response) => {
        if (response.status) {
            $('#photo_form_id').val(purchaseId);
            $('#photoModal').modal('show');

            // Очищаем предыдущие превью фотографий
            $('#selectedPhotos').addClass("row row-cols-1 row-cols-md-3 g-4").empty();

            var photos = response.photos;
            for (var i = 0; i < photos.length; i++) {
                var photoDiv = $('<div>')
                    .addClass('col')
                    .appendTo('#selectedPhotos');

                var cardDiv = $('<div>')
                    .addClass('card')
                    .appendTo(photoDiv);

                var imgElement = $('<img>')
                    .addClass('card-img-top mr-2 mb-2')
                    .attr('src', photos[i].url)
                    .attr('height', '250')
                    .appendTo(cardDiv);

                var removeButton = $('<button>')
                    .addClass('col-6 d-grid mx-auto content-md-center btn btn-outline-danger btn-sm remove-photo')
                    .text('Remove')
                    .attr('data-index', photos[i].id)
                    .appendTo(cardDiv);

                imgElement.after(removeButton);
            }
        }
    }).catch((response) => {
        console.log(response);
    });
}
