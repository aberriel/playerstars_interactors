from playerstars_interactors.utils.upload_photos import \
    check_and_remove_metadata


fake_png = "data:image/png;base64," \
           "OIAHDOIGAIHSOIUHDFOAIUHSOIUHQISUHAIUDHAIUS"
fake_jpg = "data:image/jpg;base64," \
           "OIAHDOIGAIHSOIUHDFOAIUHSOIUHQISUHAIUDHAIUS"

fake_no_header = "OIAHDOIGAIHSOIUHDFOAIUHSOIUHQISUHAIUDHAIUS"


def test_check_metadata():
    assert check_and_remove_metadata(fake_png) == \
        ("OIAHDOIGAIHSOIUHDFOAIUHSOIUHQISUHAIUDHAIUS", 'png')
    assert check_and_remove_metadata(fake_jpg) == \
        ("OIAHDOIGAIHSOIUHDFOAIUHSOIUHQISUHAIUDHAIUS", 'jpg')

    assert check_and_remove_metadata(fake_no_header) == \
        ("OIAHDOIGAIHSOIUHDFOAIUHSOIUHQISUHAIUDHAIUS", 'jpg')
