let unsavedChanges = false;

window.onbeforeunload = function() {
    if (unsavedChanges) {
        return "";
    }
}

$(function () {
    $('#start-time-picker').bootstrapMaterialDatePicker({
        date: true,
        format: 'MMM DD h:mm a',
        switchOnClick: false,
        shortTime: true,
        minDate: moment($('#meeting-start-date').val())
    }).on('change', function(e, date) {
        unsavedChanges = true;
        $('#start-time').val(date.format('YYYY-MM-DD HH:MM'));
    });

    $('#end-time-picker').bootstrapMaterialDatePicker({
        date: true,
        format: 'MMM DD h:mm a',
        switchOnClick: false,
        shortTime: true,
        minDate: moment($('#meeting-start-date').val()),
        maxDate: moment($('#meeting-end-date').val())
    }).on('change', function(e, date) {
        unsavedChanges = true;
        $('#end-time').val(date.format('YYYY-MM-DD HH:MM'));
    });
});

function onMeetingSelect(e) {
    console.log(e);
}

function onSubmit() {
    unsavedChanges = false;
    const st = $('#start-time').val();
    const et = $('#end-time').val();
    console.log('st', st, 'et', et);

    document.getElementById('avlb-form').submit();
}