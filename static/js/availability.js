let unsavedChanges = false;

window.onbeforeunload = function() {
    if (unsavedChanges) {
        return "";
    }
}

$(function () {
    $('#start-time-picker').datetimepicker();
    $('#end-time-picker').datetimepicker({
        useCurrent: false //Important! See issue #1075
    });
    $("#start-time-picker").on("dp.change", function (e) {
        $('#end-time-picker').data("DateTimePicker").minDate(e.date);
    });
    $("#end-time-picker").on("dp.change", function (e) {
        $('#start-time-picker').data("DateTimePicker").maxDate(e.date);
    });
});

$('#start-time-picker').on('dp.change', function(e) {
    // console.log('date: ', e.date);
    // console.log('previous date: ', e.oldDate);
    unsavedChanges = true;
});

$('#end-time-picker').on('dp.change', function(e) {
    // console.log('date: ', e.date);
    // console.log('previous date: ', e.oldDate);
    unsavedChanges = true;
});

function onSubmit() {
    const st = $('#start-time-picker').data('DateTimePicker').date();
    const et = $('#end-time-picker').data('DateTimePicker').date();

    if (!st) {
        $('#start-time-error').removeClass('d-none');
        $('#start-time-form-group').addClass('has-error');
        return;
    } else {
        $('#start-time-error').addClass('d-none');
        $('#start-time-form-group').removeClass('has-error');
    }

    if (!et) {
        $('#end-time-error').removeClass('d-none');
        $('#end-time-form-group').addClass('has-error');
        return;
    } else {
        $('#end-time-error').addClass('d-none');
        $('#end-time-form-group').removeClass('has-error');
    }


    const tslots_str = $('#time_slots_json').text();
    const tslots = JSON.parse(tslots_str);
    for (const slot of tslots) {
        const slot_start = moment(slot.start_time);
        const slot_end = moment(slot.end_time);

        if (et.isAfter(slot_start) && st.isBefore(slot_end)) {
            const msg = "This time overlaps with a time slot for meeting " +
                slot.meeting.id + " (" + slot.meeting.description + ") from " +
                slot_start.format('MMMM Do hh:mm a') + " to " + slot_end.format('MMMM Do hh:mm a') +
                ". Please select a time frame that does not overlap with one previously entered.";
            alert(msg);
            return;
        }
    }

    $('#start-time').val(st.format('YYYY-MM-DD HH:mm'));
    $('#end-time').val(et.format('YYYY-MM-DD HH:mm'));

    unsavedChanges = false;

    document.getElementById('avlb-form').submit();
}

function onDelete(id, st, et) {
    $('#delete-start-time').text(st);
    $('#delete-end-time').text(et);
    $('#delete-id').val(id);
    $('#delete-confirm').modal('show');
}

function onDeleteConfirm() {
    document.getElementById('delete-form').submit();
}

$('#delete-confirm').on('shown.bs.modal', function () {
    $('#delete-cancel').trigger('focus');
});
