insert_history_regime = """INSERT INTO history_regimes (
                            line_id, product_name, regime,  
                            over_alko_volume, over_bottles_counts, beg_time)
                                        VALUES ($1, $2, $3, $4, $5, $6)"""

add_end_time_regime = """UPDATE history_regimes SET bottles_count=$1, alko_volume=$2, end_time=$3 
                                                WHERE line_id=$4 and beg_time=$5"""


insert_intervening_data = """INSERT INTO intervening_data_lines (line_id, over_alko_volume, over_bottles_counts)
                                                        VALUES ($1, $2, $3)"""

select_users_bot = "SELECT * FROM users"
select_entry = """SELECT line_id FROM history_regimes WHERE line_id=$1 and beg_time=$2"""
select_lines = """SELECT * FROM lines"""


select_regimes_per_period = """SELECT * FROM history_regimes WHERE beg_time
                                                BETWEEN $1 AND $2 
                                                AND line_id = Any($3::BIGINT[])
                                                AND end_time IS NOT NULL
                                ORDER BY beg_time"""

select_regime_line = """SELECT * FROM history_regimes WHERE beg_time = $1 AND line_id = $2"""

select_interv_data = """SELECT * FROM intervening_data_lines WHERE line_id = $1 
                                                        AND create_time >= $2
                                                        AND create_time < $3
                                            ORDER BY create_time"""

select_not_closed_regimes = """SELECT * FROM history_regimes WHERE beg_time
                                BETWEEN $1 AND $2
                                AND end_time IS NULL
                                ORDER BY beg_time"""

# PARAMETERS
not_consider_flash = "regime != 1"