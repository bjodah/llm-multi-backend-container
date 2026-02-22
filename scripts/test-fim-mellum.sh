
main() {
    set -x
    curl -s -X POST ${1:-"localhost:8650"}/v1/completions -H "Content-Type: application/json" -d@fim-mellum.json
}
{
    cd "$(dirname "$(realpath "$0")")"
    main "$@"
    exit $?
}
