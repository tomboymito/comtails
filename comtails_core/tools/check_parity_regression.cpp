#include <cmath>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

struct Row {
    std::string scenario;
    long long count;
    long long seed;
    long long nevent;
    double elapsed_ms;
    double flux_sum;
    double depth_sum;
    double depth_nuc;
    double vnorm0;
};

int main(int argc, char** argv) {
    const std::string path = (argc > 1) ? argv[1] : "comtails_core/parity_dataset.csv";
    std::ifstream in(path);
    if (!in.is_open()) {
        std::cerr << "Не удалось открыть CSV: " << path << "\n";
        return 1;
    }

    std::string line;
    if (!std::getline(in, line)) {
        std::cerr << "CSV пустой: " << path << "\n";
        return 1;
    }

    std::vector<Row> rows;
    while (std::getline(in, line)) {
        if (line.empty()) {
            continue;
        }

        std::stringstream ss(line);
        std::string token;
        Row r{};

        std::getline(ss, r.scenario, ',');
        std::getline(ss, token, ','); r.count = std::stoll(token);
        std::getline(ss, token, ','); r.seed = std::stoll(token);
        std::getline(ss, token, ','); r.nevent = std::stoll(token);
        std::getline(ss, token, ','); r.elapsed_ms = std::stod(token);
        std::getline(ss, token, ','); r.flux_sum = std::stod(token);
        std::getline(ss, token, ','); r.depth_sum = std::stod(token);
        std::getline(ss, token, ','); r.depth_nuc = std::stod(token);
        std::getline(ss, token, ','); r.vnorm0 = std::stod(token);

        rows.push_back(r);
    }

    if (rows.size() != 3) {
        std::cerr << "Ожидалось 3 сценария (small/medium/large), получено: " << rows.size() << "\n";
        return 1;
    }

    const double v0 = rows[0].vnorm0;
    for (const auto& r : rows) {
        if (!(r.flux_sum > 0.0 && r.depth_sum > 0.0)) {
            std::cerr << "Некорректные фотометрические метрики в сценарии: " << r.scenario << "\n";
            return 1;
        }
        if (std::fabs(r.vnorm0 - v0) > 1e-12) {
            std::cerr << "Нарушена детерминированность модуля скорости в сценарии: " << r.scenario << "\n";
            return 1;
        }
    }

    if (!(rows[0].elapsed_ms < rows[1].elapsed_ms && rows[1].elapsed_ms < rows[2].elapsed_ms)) {
        std::cerr << "Время выполнения не монотонно по размеру сценария\n";
        return 1;
    }

    std::cout << "Parity regression check: OK\n";
    std::cout << "CSV: " << path << "\n";
    return 0;
}
