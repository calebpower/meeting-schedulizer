$(function () {
    $('#start-time-picker').bootstrapMaterialDatePicker({
        date: true,
        format: 'MMM DD h:mm a',
        switchOnClick: false,
        shortTime: true,
        minDate: moment()
    }).on('change', function(e, date) {
        $('#end-time-picker').bootstrapMaterialDatePicker('setMinDate', date);
        $('#start-time').val(date.format('YYYY-MM-DD HH:MM'));
    });

    $('#end-time-picker').bootstrapMaterialDatePicker({
        date: true,
        format: 'MMM DD h:mm a',
        switchOnClick: false,
        shortTime: true,
        minDate: moment()
    }).on('change', function(e, date) {
        $('#start-time-picker').bootstrapMaterialDatePicker('setMaxDate', date);
        $('#end-time').val(date.format('YYYY-MM-DD HH:MM'));
    });
});

function onMeetingSelect(e) {
    console.log(e);
}

function onSubmit() {
    const st = $('#start-time').val();
    const et = $('#end-time').val();
    console.log('st', st, 'et', et);
    
    document.getElementById('avlb-form').submit();
}