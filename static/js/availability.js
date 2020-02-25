$(function () {
    $('#start-time').bootstrapMaterialDatePicker({
        date: false,
        format: 'h:mm a',
        switchOnClick: false,
        shortTime: true
    });

    $('#end-time').bootstrapMaterialDatePicker({
        date: false,
        format: 'h:mm a',
        switchOnClick: false,
        shortTime: true
    });
});

function onMeetingSelect(mtg) {
    console.log(mtg);

    $('#selected-meeting').text(mtg);
    $('#meeting-not-selected').hide();
    $('#meeting-selected').show();
}