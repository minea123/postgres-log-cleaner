 truncate table t_std_data_ais;
insert into
    t_std_data_ais
SELECT
    "v_student_profile_lists"."id",
    "v_student_profile_lists"."student_id" AS "student_id",
    "v_student_profile_lists"."campus_id",
    "v_student_profile_lists"."year_id",
    "v_student_profile_lists"."term_id",
    "v_student_profile_lists"."class_id",
    "v_student_profile_lists"."shift_id",
    "v_student_profile_lists"."image",
    "v_student_profile_lists"."image_ais",
    "v_student_profile_lists"."school_id",
    "main_class"."main_class_name",
    "fullname",
    "fullname_kh",
    "enroll_student_code",
    "gender",
    "phone_number",
    "days"."name" as study_day,
    "main_class"."year_id" as main_class_year_id,
    inv.id as inv_id,
    inv.start_date,
    inv.end_date,
    inv.receipt_date,
    inv.payment_status
FROM
    "v_student_profile_lists"
        INNER JOIN (
        SELECT
            inv.ID,
            invd.item_type,
            start_date,
            end_date,
            inv_receipt.receipt_date::DATE,
                inv.payment_status,
            invrt.receipt_type,
            invoice_detail_term.term,
            invoice_detail_term.term_id,
            inv.student_id,
            inv.program_id,
            inv.school_id,invoice_detail_term.year,invoice_detail_term.year_id
        FROM
            sch_pre_invoices AS inv
                INNER JOIN sch_pre_invoice_details AS invd ON ( invd.invoice_id = inv.ID AND invd.item_type IN ( 'tuition_fee', 'elective_class' ) AND invd.deleted_at IS NULL )
                INNER JOIN sch_pre_invoice_detail_terms AS invoice_detail_term ON ( invoice_detail_term.pre_invoice_detail_id = invd.ID )
                INNER JOIN sch_pre_invoice_receipts AS inv_receipt ON (inv_receipt.invoice_id = inv.id)
                INNER JOIN sch_pre_invoice_receipt_number_by_type AS invrt ON ( invrt.invoice_id = inv.ID AND invrt.receipt_type = 'ais_tuition_fee' AND (invrt.receipt_payment_status IS NULL OR invrt.receipt_payment_status='refunded'))
        WHERE
            inv.deleted_at is NULL and  "inv"."invoice_status" = 'verified'
          AND payment_status IN ('paid','partial')
    ) inv ON ("inv"."student_id" = "v_student_profile_lists"."student_id"
        AND inv.school_id = v_student_profile_lists.school_id
        and inv.year_id =v_student_profile_lists.year_id )
        INNER JOIN (
        SELECT MAX
               ( ID ) AS max_enrollment_id
        FROM
            v_student_profile_lists
        WHERE
            (
                ( class_status ) :: TEXT = ANY ( ARRAY [ ( 'active' :: CHARACTER VARYING ) :: TEXT, ( 'demote' :: CHARACTER VARYING ) :: TEXT, ( 'promote' :: CHARACTER VARYING ) :: TEXT ] )
    ) and school_id = 2
GROUP BY
    student_id,
    year_id,
    program_id,
    level_id
    ) AS t_ais_enroll ON "t_ais_enroll"."max_enrollment_id" = "v_student_profile_lists"."id"
    INNER JOIN (
    SELECT DISTINCT ON
    ( student_id, year_id ) student_id,
    CLASS AS main_class_name,
    year_id,
    class_status,
    is_elective_grade,
    is_ais_level
    FROM
    v_student_profile_lists
    WHERE
    ( ( is_elective_grade = FALSE ) AND ( is_ais_level = FALSE ) )  and school_id = 2
    ORDER BY
    student_id,
    year_id,
    ID DESC
    ) AS "main_class" ON "main_class"."student_id" = "v_student_profile_lists"."student_id"
    AND main_class.year_id = v_student_profile_lists.year_id
    LEFT JOIN "day_study_day" ON "day_study_day"."study_day_id" = "v_student_profile_lists"."study_day_id"
    LEFT JOIN "days" ON "day_study_day"."day_id" = "days"."id"
WHERE
    "v_student_profile_lists"."deleted_at" IS NULL
  and v_student_profile_lists.is_elective_grade = FALSE
group by
    "v_student_profile_lists"."id",
    "v_student_profile_lists"."student_id",
    "v_student_profile_lists"."campus_id",
    "v_student_profile_lists"."year_id",
    "v_student_profile_lists"."term_id",
    "v_student_profile_lists"."class_id",
    "v_student_profile_lists"."shift_id",
    "v_student_profile_lists"."class",
    "v_student_profile_lists"."image",
    "v_student_profile_lists"."image_ais",
    "v_student_profile_lists"."school_id",
    "fullname",
    "fullname_kh",
    "enroll_student_code",
    "gender",
    "image",
    "phone_number",
    "days"."name",
    "main_class"."main_class_name",
    "main_class"."year_id",
    inv.id,
    inv.start_date,
    inv.end_date,
    inv.receipt_date,
    inv.payment_status