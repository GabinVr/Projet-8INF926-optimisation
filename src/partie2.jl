using Printf

function power_turbine(Q, H, turbine_id)
    if Q == 0.0
        return 0.0
    end
    if turbine_id == 1
        
        return -90.258 + 0.6049 * Q + 3.0334 * H - 0.0029 * Q^2 + 0.0139 * Q * H - 0.0569 * H^2
    elseif turbine_id == 2
        
        Qn = (Q - 134.2) / 10.39
        Hn = (H - 34.11) / 0.429
        return 41.736 + 3.5717 * Qn + 0.4274 * Hn - 0.2597 * Qn^2 + 0.0525 * Qn * Hn + 0.0044 * Hn^2
    elseif turbine_id == 3
        
        Qn = (Q - 136.2) / 4.029
        Hn = (H - 34.14) / 0.4976
        return 40.9 + 1.2454 * Qn + 0.5479 * Hn - 0.0659 * Qn^2 - 0.0130 * Qn * Hn +
               0.0035 * Hn^2 - 0.0022 * Qn^3 + 0.0037 * Qn^2 * Hn + 0.0188 * Qn * Hn^2
    elseif turbine_id == 4
        
        return -74.121 + 0.6572 * Q + 1.7094 * H - 0.0029 * Q^2 + 0.0141 * Q * H - 0.0355 * H^2
    elseif turbine_id == 5
        
        return -234.15 + 1.9425 * Q + 5.9587 * H - 0.0017 * Q^2 - 0.0341 * Q * H
    else
        error("ID turbine invalide: $turbine_id")
    end
end

function h_net(h_amont, h_aval, Q)
    return (h_amont - h_aval) - (0.5e-5 * Q^2)
end

function calc_h_aval(Qtotal)
    
    x = (Qtotal - 642.5) / 171.4

    
    p1 = -0.0419
    p2 = 0.8844
    p3 = 103.89

    return p1 * x^2 + p2 * x + p3
end

function optimize_turbines(Qtotal, h_amont)
    n_turbines = 5
    Q_max = 160.0
    delta_q = 5.0
    h_aval = calc_h_aval(Qtotal)

    
    q_target = floor(Int, Qtotal / delta_q) * delta_q
    states = collect(0.0:delta_q:q_target)

    n_states = length(states)
    dp = fill(-Inf, n_states, n_turbines + 1)
    decisions = zeros(Float64, n_states, n_turbines)

    
    dp[1, n_turbines + 1] = 0.0

    for t in n_turbines:-1:1
        for (i, q) in enumerate(states)
            max_power = -Inf
            best_decision = 0.0

            upper = min(q, Q_max)
            for q_turbine in 0.0:delta_q:upper

                remaining_q = q - q_turbine
                j = floor(Int, remaining_q / delta_q) + 1
                if 1 <= j <= n_states && isfinite(dp[j, t + 1])
                    head = h_net(h_amont, h_aval, q_turbine)
                    power = power_turbine(q_turbine, head, t) + dp[j, t + 1]
                    if power > max_power
                        max_power = power
                        best_decision = q_turbine
                    end
                end
            end

            dp[i, t] = max_power
            decisions[i, t] = best_decision
        end
    end

    solution = zeros(Float64, n_turbines)
    remaining = q_target
    for t in 1:n_turbines
        idx = floor(Int, remaining / delta_q) + 1
        q_t = decisions[idx, t]
        solution[t] = q_t
        remaining -= q_t
    end

    return solution, dp[end, 1], q_target
end

parse_fr_float(s::AbstractString) = parse(Float64, replace(strip(s), ',' => '.'))

function evaluate_dataset(csv_path::String; max_rows::Int = 100)
    open(csv_path, "r") do io
        header = readline(io)
        if isempty(header)
            error("CSV vide: $csv_path")
        end

        n = 0
        sum_signed_diff = 0.0
        sum_abs_diff = 0.0
        sum_sq_diff = 0.0
        min_diff = Inf
        max_diff = -Inf
        sum_active_pred = 0
        sum_active_real = 0
        total_solve_ns = Int128(0)
        min_solve_ns = typemax(Int64)
        max_solve_ns = Int64(0)
        sum_ape = 0.0
        n_mape = 0
        interval_hours = 2.0 / 60.0

        for line in eachline(io)
            isempty(strip(line)) && continue
            cols = split(line, ';')
            length(cols) < 15 && continue

            q_total = parse_fr_float(cols[2])
            h_amont = parse_fr_float(cols[5])
            q1_real = parse_fr_float(cols[6])
            q2_real = parse_fr_float(cols[8])
            q3_real = parse_fr_float(cols[10])
            q4_real = parse_fr_float(cols[12])
            q5_real = parse_fr_float(cols[14])

            real_total_power = parse_fr_float(cols[7]) + parse_fr_float(cols[9]) +
                               parse_fr_float(cols[11]) + parse_fr_float(cols[13]) +
                               parse_fr_float(cols[15])

            t0_ns = time_ns()
            pred_flows, pred_power, q_used = optimize_turbines(q_total, h_amont)
            elapsed_ns = time_ns() - t0_ns
            if !isfinite(pred_power)
                @printf("Ligne %d: solution infeasible (Qtotal=%.2f, Qcible=%.2f)\n", n + 2, q_total, q_used)
                continue
            end

            diff = pred_power - real_total_power
            n += 1
            sum_signed_diff += diff
            sum_abs_diff += abs(diff)
            sum_sq_diff += diff^2
            min_diff = min(min_diff, diff)
            max_diff = max(max_diff, diff)
            total_solve_ns += elapsed_ns
            min_solve_ns = min(min_solve_ns, elapsed_ns)
            max_solve_ns = max(max_solve_ns, elapsed_ns)

            active_pred = count(q -> q > 0.0, pred_flows)
            active_real = count(q -> q > 0.0, (q1_real, q2_real, q3_real, q4_real, q5_real))
            sum_active_pred += active_pred
            sum_active_real += active_real

            if real_total_power != 0.0
                sum_ape += abs(diff) / abs(real_total_power)
                n_mape += 1
            end

            if n <= 5
                @printf("Ligne %d | Q=%.2f -> Pred=%.2f MW, Reel=%.2f MW, Diff=%.2f MW, Turbines actives (P/R)=%d/%d\n",
                        n + 1, q_total, pred_power, real_total_power, diff, active_pred, active_real)
            end

            n >= max_rows && break
        end

        if n == 0
            error("Aucune ligne exploitable lue dans $csv_path")
        end

        mean_signed = sum_signed_diff / n
        mae = sum_abs_diff / n
        rmse = sqrt(sum_sq_diff / n)
        mean_active_pred = sum_active_pred / n
        mean_active_real = sum_active_real / n
        mean_solve_ms = (total_solve_ns / n) / 1e6
        min_solve_ms = min_solve_ns / 1e6
        max_solve_ms = max_solve_ns / 1e6
        mape = n_mape > 0 ? (sum_ape / n_mape) * 100.0 : NaN
        gain_total_mwh = sum_signed_diff * interval_hours
        gain_abs_total_mwh = sum_abs_diff * interval_hours

        println("\n=== Resume test partie 2 ===")
        @printf("Fichier: %s\n", csv_path)
        @printf("Lignes evaluees: %d\n", n)
        @printf("Biais moyen (pred - reel): %.4f MW\n", mean_signed)
        @printf("MAE: %.4f MW\n", mae)
        @printf("RMSE: %.4f MW\n", rmse)
        @printf("Difference minimale (pred - reel): %.4f MW\n", min_diff)
        @printf("Difference maximale (pred - reel): %.4f MW\n", max_diff)
        @printf("MAPE: %.4f %%\n", mape)
        @printf("Nb moyen de turbines actives (Pred): %.3f\n", mean_active_pred)
        @printf("Nb moyen de turbines actives (Reel): %.3f\n", mean_active_real)
        @printf("Temps de resolution moyen: %.4f ms/ligne\n", mean_solve_ms)
        @printf("Temps min/max de resolution: %.4f / %.4f ms\n", min_solve_ms, max_solve_ms)
        @printf("Gain total d'energie (Pred - Reel): %.4f MWh\n", gain_total_mwh)
        @printf("Ecart energetique absolu cumule: %.4f MWh\n", gain_abs_total_mwh)
    end
end

function run_single(q_total::Float64, h_amont::Float64)
    h_aval = calc_h_aval(q_total)
    flows, power, q_target = optimize_turbines(q_total, h_amont)
    println("Repartition optimale des debits:")
    for (i, q) in enumerate(flows)
        @printf("  Turbine %d: %.1f m3/s\n", i, q)
    end
    @printf("h_aval predit: %.4f m\n", h_aval)
    @printf("Q cible discretise: %.1f m3/s\n", q_target)
    @printf("Puissance totale predite: %.2f MW\n", power)
end

function main()
    if !isempty(ARGS) && ARGS[1] == "single"
        if length(ARGS) != 3
            error("Usage single: julia test_partie2.jl single Qtotal h_amont")
        end
        q_total = parse(Float64, ARGS[2])
        h_amont = parse(Float64, ARGS[3])
        run_single(q_total, h_amont)
        return
    end

    default_csv = normpath(joinpath(@__DIR__, "..", "..", "DataProjet2026.csv"))
    csv_path = isempty(ARGS) ? default_csv : ARGS[1]
    max_rows = length(ARGS) >= 2 ? parse(Int, ARGS[2]) : 100

    evaluate_dataset(csv_path; max_rows = max_rows)
end

main()
