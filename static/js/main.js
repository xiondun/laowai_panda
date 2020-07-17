$(document).ready(function () {
    //  $('#my_video').RTOP_VideoPlayer({
    //     showFullScreen: true,
    //     showTimer: true,
    //     showSoundControl: true,
    // });

    $("#video-player").videoPopup({
        autoplay: 1,
        controlsColor: 'white',
        showVideoInformations: 0,
        width: 1000,
        customOptions: {
            rel: 0,
            end: 60
        }
    });
})