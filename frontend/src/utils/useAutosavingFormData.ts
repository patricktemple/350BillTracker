import { useState } from 'react';
import useInterval from '@restart/hooks/useInterval';

const SAVE_INTERVAL_MS = 2000;

// TODO: Unit test this thing

// Tracks state for an arbitrary object just like useState, but with extra behavior to
// create an automatically saving form like Google docs. Every few seconds, if the state
// was recently modified, it will HTTP PUT the state to the provided path to save it.
//   - path: the API path that accepts the state as the request body of a PUT
//   - initialData: initial data for the state
//
// Returns [data, setData, saveStatus]. "data" and "setData" are just like the usual from
// useState. "saveStatus" is a string describing the current status of the save.
export default function useAutosavingFormData<T>(
  path: string,
  initialData: T
): [T, (newData: T) => void, string] {
  const [localSaveVersion, setLocalSaveVersion] = useState<number>(0);
  const [remoteSaveVersion, setRemoteSaveVersion] = useState<number>(0);
  const [saveInProgress, setSaveInProgress] = useState<boolean>(false);
  const [formState, setFormState] = useState<T>(initialData);
  const [saveError, setSaveError] = useState<boolean>(false);

  function setFormDataState(newData: T) {
    setLocalSaveVersion(localSaveVersion + 1);
    setFormState(newData);
  }

  function maybeSaveUpdates() {
    if (localSaveVersion > remoteSaveVersion && !saveInProgress) {
      setSaveInProgress(true);
      fetch(path, {
        method: 'PUT',
        body: JSON.stringify(formState),
        headers: {
          'Content-Type': 'application/json'
        }
      })
        .then((response) => {
          if (response.status == 200) {
            return response.json();
          } else {
            setSaveInProgress(false);
            throw new Error('Failed to save form data');
          }
        })
        .then((response) => {
          setSaveInProgress(false);
          setRemoteSaveVersion(localSaveVersion);
          setSaveError(false);
        })
        .catch(() => {
          setSaveInProgress(false);
          setSaveError(true);
        });
    }
  }

  useInterval(() => maybeSaveUpdates(), SAVE_INTERVAL_MS);

  let saveStatus = '';
  if (saveError) {
    saveStatus = 'Failed to save';
  } else if (localSaveVersion > remoteSaveVersion) {
    saveStatus = 'Draft';
  } else if (saveInProgress) {
    saveStatus = 'Saving...';
  } else if (remoteSaveVersion > 0) {
    saveStatus = 'Saved';
  }

  return [formState, setFormDataState, saveStatus];
}
