from src.constants.constants import *
from src.pipeline.ipynb_pipeline_detector import IpynbPipelineDetector
from src.utils.file_reader import FileReader, NotebookReader

if __name__ == '__main__':
    # FileReader(dataset_base_path)
    all_ipynb_paths = NotebookReader(dataset_base_path).all_ipynb_paths
    pipeline = IpynbPipelineDetector(all_ipynb_paths, base_path)
    # pipeline.remove_non_parsable_files()
    df = pipeline.get_results()
    cols = ["path", "competitionId", "pipeline_step", "keyword", "cell_no", "line_no", "column_no", "parameters"]
    df.columns = cols
    df.to_csv(os.path.join(base_path, res_folder, pipeline_csv_file), columns=cols, index=False, encoding='utf-8')
