monthly_summery_query = """
SELECT 
    i.mess_no,
    i.inmate_name,
    i.department,  -- Adjust if needed
    i.join_count,  -- From the first query,
    i.is_ablc,
    COALESCE(gl.total_guest_count, 0) AS guest_count,  -- From the second query, treat NULL as 0
    COALESCE(gl.total_sg_count, 0) AS sg_count  -- From the second query, treat NULL as 0
FROM 
    (
        -- First query: Inmate counts for mess in status
        SELECT 
            i.mess_no,
            i.inmate_name,
            i.department,  -- Adjust if needed,
            i.is_ablc,
            COUNT(ms.in_status) AS join_count
        FROM inmates i
        JOIN mess_status ms ON i.mess_no = ms.mess_no
            AND ms.in_status = 'in'
            AND ms.update_date BETWEEN %s AND %s
        GROUP BY i.mess_no, i.inmate_name, i.department
    ) i
LEFT JOIN 
    (
        -- Second query: Guest counts from guest_logs
        SELECT 
            mess_no, 
            SUM(guest_count) AS total_guest_count, 
            SUM(sg_count) AS total_sg_count
        FROM guest_logs
        GROUP BY mess_no
    ) gl
ON i.mess_no = gl.mess_no
ORDER BY i.mess_no, i.inmate_name;
"""