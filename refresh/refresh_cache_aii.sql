truncate table t_std_data;
insert into
    t_std_data
SELECT
    vspl.ID,
    vspl.old_enrollment_id,
    vspl.student_id AS student_id,
    vspl.campus_id,
    vspl.year_id,
    vspl.term_id,
    vspl.class_id,
    vspl.shift_id,
    vspl.image,
    vspl.image_ais,
    vspl.school_id,
    vspl.student_ma,
    vspl.study_time_id,
    vspl.ma_study_time_id,
    vspl.study_day_id,
    vspl.enroll_type,
    vspl.is_multiple_study_time,
    fullname,
    fullname_kh,
    enroll_student_code,
    gender,
    phone_number,
    days.NAME as study_day,
    inv.start_date,
    inv.end_date,
    inv.term_id as invoice_term_id
FROM
    v_student_profile_lists AS vspl
        INNER JOIN (
        SELECT
            inv.ID,
            invd.item_type,
            start_date,
            end_date,
            inv_receipt.receipt_date :: DATE,
                inv.payment_status,
            invrt.receipt_type,
            invoice_detail_term.term,
            invoice_detail_term.term_id,
            inv.student_id,
            inv.program_id,
            inv.school_id
        FROM
            sch_pre_invoices AS inv
                INNER JOIN sch_pre_invoice_details AS invd ON (
                invd.invoice_id = inv.ID
                    AND invd.item_type IN ('tuition_fee', 'elective_class')
                    AND invd.deleted_at IS NULL
                )
                INNER JOIN sch_pre_invoice_detail_terms AS invoice_detail_term ON (
                invoice_detail_term.pre_invoice_detail_id = invd.ID
                )
                INNER JOIN sch_pre_invoice_receipts AS inv_receipt ON (inv_receipt.invoice_id = inv.id)
                INNER JOIN sch_pre_invoice_receipt_number_by_type AS invrt ON (
                invrt.invoice_id = inv.ID
                    AND invrt.receipt_type = 'aii_tuition_fee'
                    AND (
                    invrt.receipt_payment_status IS NULL
                        OR invrt.receipt_payment_status = 'refunded'
                    )
                )
        WHERE
            inv.deleted_at is NULL
          and "inv"."invoice_status" = 'verified'
          AND payment_status IN ('paid', 'partial')
    ) as inv ON (
        inv.student_id = vspl.student_id
            AND inv.program_id = vspl.program_id
            AND inv.school_id = vspl.school_id
            and inv.term_id = vspl.term_id
        )
        INNER JOIN (
        SELECT
            MAX (ID) AS max_enrollment_id
        FROM
            v_student_profile_lists
        WHERE
            class_status IN ('active', 'demote', 'promote', 'assessment')
        GROUP BY
            student_id,
            term_id,
            program_id
    ) AS tae ON tae.max_enrollment_id = vspl.ID
        LEFT JOIN day_study_day AS dsd ON dsd.study_day_id = vspl.study_day_id
        LEFT JOIN days ON dsd.day_id = days.ID
WHERE
    vspl.class_status IN ('promote', 'demote', 'active', 'assessment')
  AND vspl.deleted_at IS NULL
  and vspl.school_id = 1;