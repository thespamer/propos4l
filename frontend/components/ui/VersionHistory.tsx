import React from 'react';
import { format } from 'date-fns';

interface Version {
  version_number: number;
  created_at: string;
  created_by: string;
  version_notes: string;
}

interface VersionHistoryProps {
  versions: Version[];
  currentVersion: number;
  onCompare: (v1: number, v2: number) => void;
  onViewVersion: (version: number) => void;
}

export const VersionHistory: React.FC<VersionHistoryProps> = ({
  versions,
  currentVersion,
  onCompare,
  onViewVersion,
}) => {
  const [selectedVersions, setSelectedVersions] = React.useState<number[]>([]);

  const handleVersionSelect = (version: number) => {
    if (selectedVersions.includes(version)) {
      setSelectedVersions(selectedVersions.filter(v => v !== version));
    } else if (selectedVersions.length < 2) {
      setSelectedVersions([...selectedVersions, version]);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-lg font-semibold mb-4">Histórico de Versões</h3>
      
      {selectedVersions.length === 2 && (
        <button
          onClick={() => onCompare(selectedVersions[0], selectedVersions[1])}
          className="mb-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Comparar Versões
        </button>
      )}

      <div className="space-y-4">
        {versions.map((version) => (
          <div
            key={version.version_number}
            className={`p-4 border rounded-lg ${
              version.version_number === currentVersion ? 'border-blue-500' : 'border-gray-200'
            } ${selectedVersions.includes(version.version_number) ? 'bg-blue-50' : ''}`}
          >
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium">
                  Versão {version.version_number}
                  {version.version_number === currentVersion && (
                    <span className="ml-2 text-sm text-blue-500">(Atual)</span>
                  )}
                </h4>
                <p className="text-sm text-gray-500">
                  {format(new Date(version.created_at), 'dd/MM/yyyy HH:mm')}
                </p>
                <p className="text-sm text-gray-600">Por: {version.created_by}</p>
              </div>
              <div className="space-x-2">
                <button
                  onClick={() => handleVersionSelect(version.version_number)}
                  className={`px-3 py-1 text-sm rounded ${
                    selectedVersions.includes(version.version_number)
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  Selecionar
                </button>
                <button
                  onClick={() => onViewVersion(version.version_number)}
                  className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
                >
                  Visualizar
                </button>
              </div>
            </div>
            {version.version_notes && (
              <p className="mt-2 text-sm text-gray-600">{version.version_notes}</p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
