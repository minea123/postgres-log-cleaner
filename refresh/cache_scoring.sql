truncate table  t_scoring_ais_cache;
insert  into t_scoring_ais_cache
SELECT DISTINCT
    vspl.student_id,
    vspl.enroll_student_code AS student_code,
    vspl.fullname,
    vspl.fullname_kh,
    vspl.CLASS,
    vspl.class_kh,
    vspl.gender,
    vspl.LEVEL,
    vspl.is_ais_level,
    vspl.is_mna,
    vspl.school_id,
    vspl.year_id,
    vspl.campus_id,
    vspl.main_program_id,
    vspl.program_id,
    vspl.level_id,
    vspl.class_status,
    vspl.class_id,
    vspl.shift_id,
    LOWER ( vspl.shift_code :: TEXT ) AS shift_code,
    LOWER ( vspl.shift_pre_fix :: TEXT ) AS shift_pre_fix,
    main_class.class_main,
    CASE

        WHEN vspl.student_status = 'new' THEN
            1 ELSE 0
        END AS student_priority
FROM
    v_student_profile_lists vspl
        INNER JOIN ( SELECT MAX ( ID ) AS max_enrollment_id FROM v_student_profile_lists WHERE class_status IN ( 'active', 'demote', 'promote' ) GROUP BY student_id, class_id, program_id ) last_enr ON vspl.ID = last_enr.max_enrollment_id
        LEFT JOIN (
        SELECT
            student_id,
            main_program_id,
            CLASS AS class_main,
            year_id
        FROM
            v_student_profile_lists
        WHERE
            is_elective_grade = FALSE
          AND is_ais_level = FALSE
          AND class_status IN ( 'active', 'demote', 'promote' )
          AND school_id = 2
        GROUP BY
            student_id,
            main_program_id,
            CLASS,
            year_id
    ) main_class ON main_class.student_id = vspl.student_id
        AND vspl.main_program_id = main_class.main_program_id
        AND vspl.year_id = main_class.year_id
        INNER JOIN (
        SELECT
            inv.student_id,
            inv.payment_status,
            invoice_detail_term.year_id,
            inv.school_id
        FROM
            sch_pre_invoices AS inv
                JOIN sch_pre_invoice_details AS invd ON invd.invoice_id = inv.ID
                AND invd.item_type IN ( 'tuition_fee', 'elective_class' )
                AND invd.deleted_at
                                                            IS NULL JOIN sch_pre_invoice_detail_terms AS invoice_detail_term ON invoice_detail_term.pre_invoice_detail_id = invd.
                ID JOIN sch_pre_invoice_receipt_number_by_type AS invrt ON invrt.invoice_id = inv.ID
                AND invrt.receipt_type = 'ais_tuition_fee'
                AND ( invrt.receipt_payment_status IS NULL OR invrt.receipt_payment_status = 'refunded' )
        WHERE
            inv.invoice_status = 'verified'
          AND inv.school_id = 2
          AND inv.deleted_at IS NULL
    ) AS stu_pre_invoices ON vspl.student_id = stu_pre_invoices.student_id
        AND stu_pre_invoices.school_id = vspl.school_id
        AND stu_pre_invoices.payment_status = 'paid'
        AND vspl.year_id = stu_pre_invoices.year_id
WHERE
    vspl.school_id = 2
  AND vspl.class_status IN ( 'promote', 'demote', 'active' )